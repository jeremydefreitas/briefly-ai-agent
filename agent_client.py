"""Reusable Agents SDK client and session-scoped conversation memory."""

import asyncio
import os

from agents import (
    Agent,
    ModelBehaviorError,
    ModelSettings,
    ModelRetrySettings,
    RetryDecision,
    RetryPolicyContext,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    SQLiteSession,
)
from openai import AsyncOpenAI
from agents.mcp import MCPServer

from activity import ActivityHooks, EventSink, activity_sink, emit_activity
from mcp_client import FILES_ROOT, load_server_configs


def retry_model_call(context: RetryPolicyContext) -> RetryDecision:
    """Retry transient provider failures without replaying completed agent tools."""
    retry = (
        context.normalized.status_code in {500, 502, 503, 504}
        or context.normalized.is_timeout
        or context.normalized.is_network_error
    )
    if retry:
        emit_activity(
            "model_retry",
            f"The model service failed temporarily. Retrying ({context.attempt}/{context.max_retries})…",
        )
    return RetryDecision(retry=retry, delay=context.attempt)


class AgentClient:
    def __init__(self, mcp_servers: list[MCPServer] | None = None) -> None:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY to your NVIDIA NIM key in .env.")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=os.environ.get("OPENAI_BASE_URL", "").strip()
            or "https://integrate.api.nvidia.com/v1",
            timeout=60,
            max_retries=0,
        )
        self.agent = Agent(
            name="Assignment assistant",
            instructions=(
                "Answer clearly and concisely. Use conversation history when relevant. "
                f"Use filesystem tools for files under {FILES_ROOT}; resolve relative filenames there. "
                "Use Tavily for web searches and reading web pages; cite source URLs. "
                "Use Open-Meteo for weather information: resolve place names with geocoding "
                "before requesting weather_forecast with coordinates. Include units and local time. "
                "Use multiple tools when needed, and answer directly when tools are unnecessary. "
                "If a needed tool is unavailable or fails, explain that rather than inventing results."
            ),
            mcp_servers=mcp_servers or [],
            model=OpenAIChatCompletionsModel(
                model=os.environ.get("OPENAI_MODEL", "").strip()
                or "nvidia/nemotron-3-ultra-550b-a55b",
                openai_client=self.client,
            ),
            model_settings=ModelSettings(
                max_tokens=2048,
                retry=ModelRetrySettings(max_retries=2, policy=retry_model_call),
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            ),
        )
        self.run_config = RunConfig(tracing_disabled=True)
        self.sessions: dict[str, tuple[SQLiteSession, asyncio.Lock]] = {}
        self.mcp_names = tuple(load_server_configs())

    async def chat(self, query: str, session_id: str, on_event: EventSink | None = None) -> str:
        if session_id not in self.sessions:
            self.sessions[session_id] = (SQLiteSession(session_id), asyncio.Lock())
        session, lock = self.sessions[session_id]

        token = activity_sink.set(on_event)
        try:
            emit_activity("request_start", "Message received.")
            if lock.locked():
                emit_activity("queued", "Waiting for the previous turn in this conversation.")
            # Serialize a conversation's turns without blocking other sessions.
            async with lock:
                result = await Runner.run(
                    self.agent, query, session=session, run_config=self.run_config,
                    hooks=ActivityHooks(),
                )
            if not isinstance(result.final_output, str) or not result.final_output.strip():
                raise ModelBehaviorError("The model returned no text response.")
            return result.final_output
        finally:
            activity_sink.reset(token)

    async def mcp_status(self) -> list[dict]:
        connected = {server.name: server for server in self.agent.mcp_servers}

        async def check(name):
            state = {"name": name, "status": "unavailable", "tool_count": 0}
            server = connected.get(name)
            if server is not None and server.session is not None:
                try:
                    await asyncio.wait_for(server.session.send_ping(), timeout=3)
                    tools = await server.list_tools()
                    state.update(status="connected", tool_count=len(tools))
                except Exception:
                    pass
            if name == "tavily":
                state["mode"] = "authenticated" if os.environ.get("TAVILY_API_KEY", "").strip() else "keyless"
            return state

        return list(await asyncio.gather(*(check(name) for name in self.mcp_names)))

    async def close(self) -> None:
        for session, _ in self.sessions.values():
            session.close()
        self.sessions.clear()
        await self.client.close()
