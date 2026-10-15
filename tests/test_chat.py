"""Exercise the HTTP route and SDK memory without calling a paid API."""

import asyncio
import json
import os
import unittest
from types import SimpleNamespace
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import httpx2 as httpx
from openai import AsyncOpenAI
from agents import function_tool
from mcp import MCPError
from pydantic import ValidationError

import agent_client
from main import ChatRequest, app, chat_stream


class ChatTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.requests = []
        self.failure = None
        self.delay = 0
        self.active = 0
        self.max_active = 0
        self.content = "Mock answer"

        async def model_response(request):
            self.assertEqual(
                str(request.url), "https://integrate.api.nvidia.com/v1/chat/completions"
            )
            payload = json.loads(request.content)
            self.assertEqual(payload["model"], "nvidia/nemotron-3.5-lightning-30b-a3b")
            self.requests.append(payload)
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            try:
                await asyncio.sleep(self.delay)
                if self.failure == "timeout":
                    raise httpx.ReadTimeout("Mock timeout", request=request)
                if self.failure == "connection":
                    raise httpx.ConnectError("Mock connection failure", request=request)
                if isinstance(self.failure, int):
                    return httpx.Response(
                        self.failure,
                        json={"error": {"message": "Mock provider failure"}},
                    )
                choices = [] if self.failure == "malformed" else [{
                    "index": 0,
                    "message": {"role": "assistant", "content": self.content},
                    "finish_reason": "stop",
                }]
                return httpx.Response(200, json={
                    "id": "mock-completion",
                    "object": "chat.completion",
                    "created": 1,
                    "model": payload["model"],
                    "choices": choices,
                })
            finally:
                self.active -= 1

        self.model_responder = model_response

        def create_client(**kwargs):
            self.model_client = AsyncOpenAI(
                **kwargs,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(lambda request: self.model_responder(request))),
            )
            return self.model_client

        self.env_patch = patch.dict(os.environ, {
            "OPENAI_API_KEY": "dummy-test-key",
            "OPENAI_BASE_URL": "https://integrate.api.nvidia.com/v1",
            "OPENAI_MODEL": "nvidia/nemotron-3.5-lightning-30b-a3b",
        })
        self.client_patch = patch.object(agent_client, "AsyncOpenAI", side_effect=create_client)
        @asynccontextmanager
        async def no_mcp_servers():
            yield []
        self.mcp_patch = patch("main.connect_mcp_servers", no_mcp_servers)
        self.env_patch.start()
        self.client_patch.start()
        self.mcp_patch.start()
        self.lifespan = app.router.lifespan_context(app)
        await self.lifespan.__aenter__()
        self.http = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        )

    async def asyncTearDown(self):
        await self.http.aclose()
        await self.lifespan.__aexit__(None, None, None)
        self.assertTrue(self.model_client.is_closed())
        self.client_patch.stop()
        self.mcp_patch.stop()
        self.env_patch.stop()

    async def post(self, query, session_id="a"):
        return await self.http.post("/chat", json={"query": query, "session_id": session_id})

    async def test_response_history_and_session_isolation(self):
        first = await self.post("Remember blue")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), {"response": "Mock answer"})
        await self.post("What did I ask?")
        await self.post("Independent question", session_id="b")
        history = self.requests[1]["messages"]
        self.assertEqual(
            [m["content"] for m in history if m["role"] == "user"],
            ["Remember blue", "What did I ask?"],
        )
        self.assertIn({"role": "assistant", "content": "Mock answer"}, history)
        self.assertEqual(
            [m["content"] for m in self.requests[2]["messages"] if m["role"] == "user"],
            ["Independent question"],
        )

    async def test_invalid_requests_do_not_call_model(self):
        for body in ({}, {"query": "hi"}, {"query": " ", "session_id": "a"},
                     {"query": "hi", "session_id": " "},
                     {"query": 123, "session_id": "a"}):
            with self.subTest(body=body):
                response = await self.http.post("/chat", json=body)
                self.assertEqual(response.status_code, 422)
        self.assertEqual(self.requests, [])

    async def test_provider_errors_are_handled(self):
        for failure, status in ((401, 502), (429, 503), (500, 502),
                                ("timeout", 504), ("connection", 503), ("malformed", 502)):
            with self.subTest(failure=failure):
                self.failure = failure
                response = await self.post("Hello", session_id=str(failure))
                self.assertEqual(response.status_code, status)
                self.assertEqual(set(response.json()), {"detail"})
                self.assertNotIn("Mock provider failure", response.text)

    async def test_empty_model_response_is_rejected(self):
        self.content = ""
        self.assertEqual((await self.post("Hello")).status_code, 502)

    async def test_model_retry_after_tool_does_not_repeat_tool(self):
        calls = []
        payloads = []

        @function_tool
        def read_source() -> str:
            """Read a briefing source."""
            calls.append("read")
            return "Source evidence"

        async def responder(request):
            payloads.append(json.loads(request.content))
            if len(payloads) == 2:
                return httpx.Response(500, json={"message": "Internal server error"})
            message = {"role": "assistant", "content": "Briefing with evidence"}
            if len(payloads) == 1:
                message = {"role": "assistant", "content": None, "tool_calls": [{
                    "id": "source-call", "type": "function",
                    "function": {"name": "read_source", "arguments": "{}"},
                }]}
            return httpx.Response(200, json={
                "id": "retry-test", "object": "chat.completion", "created": 1,
                "model": "test", "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
            })

        self.model_responder = responder
        app.state.agent_client.agent.tools = [read_source]
        response = await self.http.post("/chat/stream", json={"query": "Research a briefing", "session_id": "retry-tool"})
        events = [json.loads(line) for line in response.text.splitlines()]
        self.assertEqual(events[-1]["response"], "Briefing with evidence")
        self.assertEqual(calls, ["read"])
        self.assertEqual(payloads[1], payloads[2])
        self.assertEqual(len([e for e in events if e["type"] == "model_retry"]), 1)

    async def test_persistent_model_failure_has_bounded_visible_retries(self):
        self.failure = 500
        response = await self.http.post("/chat/stream", json={"query": "Briefing", "session_id": "retry-exhausted"})
        events = [json.loads(line) for line in response.text.splitlines()]
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(len([e for e in events if e["type"] == "model_retry"]), 2)
        self.assertEqual(events[-1]["status_code"], 502)
        self.assertIn("model service failed after retries", events[-1]["message"])

    async def test_transient_timeout_recovers_and_authentication_does_not_retry(self):
        original = self.model_responder

        async def timeout_once(request):
            self.failure = "timeout" if not self.requests else None
            return await original(request)

        self.model_responder = timeout_once
        response = await self.http.post("/chat/stream", json={"query": "Briefing", "session_id": "timeout-retry"})
        events = [json.loads(line) for line in response.text.splitlines()]
        self.assertEqual(events[-1]["response"], "Mock answer")
        self.assertEqual(len(self.requests), 2)
        self.model_responder = original
        self.failure = 401
        self.assertEqual((await self.post("Hello", "auth-failure")).status_code, 502)
        self.assertEqual(len(self.requests), 3)

    async def test_mcp_discovery_errors_return_safe_responses(self):
        try:
            ChatRequest.model_validate({"query": [], "session_id": "a"})
        except ValidationError as error:
            malformed = error
        for error in (MCPError(-32603, "Mock protocol failure"), malformed):
            with self.subTest(error=type(error).__name__):
                server = AsyncMock()
                server.name = "mock-mcp"
                server.list_tools.side_effect = error
                app.state.agent_client.agent.mcp_servers = [server]
                response = await self.post("Use a tool")
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json(), {"detail": "The agent could not complete the request."})

    async def test_same_session_turns_are_ordered(self):
        self.delay = 0.02
        responses = await asyncio.gather(self.post("First"), self.post("Second"))
        self.assertTrue(all(r.status_code == 200 for r in responses))
        self.assertEqual(self.max_active, 1)
        users = [m["content"] for m in self.requests[1]["messages"] if m["role"] == "user"]
        self.assertEqual(users, ["First", "Second"])

    async def test_different_sessions_run_concurrently(self):
        self.delay = 0.02
        responses = await asyncio.gather(self.post("First", "a"), self.post("Second", "b"))
        self.assertTrue(all(r.status_code == 200 for r in responses))
        self.assertEqual(self.max_active, 2)

    async def test_missing_key_fails_at_startup(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                agent_client.AgentClient()

    async def test_stream_reports_activity_and_final_response(self):
        response = await self.http.post("/chat/stream", json={"query": "Hello", "session_id": "stream"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/x-ndjson", response.headers["content-type"])
        events = [json.loads(line) for line in response.text.splitlines()]
        self.assertEqual([e["type"] for e in events], ["request_start", "model_start", "model_end", "response"])
        self.assertEqual(events[-1]["response"], "Mock answer")
        self.assertNotIn("dummy-test-key", response.text)

    async def test_stream_delivers_first_event_before_completion(self):
        self.delay = 0.1
        response = await chat_stream(
            ChatRequest(query="Hello", session_id="live-stream"), SimpleNamespace(app=app)
        )
        first = json.loads(await asyncio.wait_for(anext(response.body_iterator), timeout=0.05))
        self.assertEqual(first["type"], "request_start")
        remaining = [json.loads(line) async for line in response.body_iterator]
        self.assertEqual(remaining[-1]["type"], "response")

    async def test_stream_reports_provider_failure(self):
        self.failure = 429
        response = await self.http.post("/chat/stream", json={"query": "Hello", "session_id": "stream-error"})
        events = [json.loads(line) for line in response.text.splitlines()]
        self.assertEqual(events[-1]["type"], "error")
        self.assertEqual(events[-1]["status_code"], 503)
        self.assertNotIn("Mock provider failure", response.text)

    async def test_status_reports_missing_servers(self):
        response = await self.http.get("/mcp/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({s["name"] for s in response.json()["servers"]}, {"filesystem", "tavily", "open-meteo"})
        self.assertTrue(all(s["status"] == "unavailable" for s in response.json()["servers"]))

    async def test_activity_is_isolated_between_concurrent_requests(self):
        self.delay = 0.02
        first, second = [], []
        client = app.state.agent_client
        await asyncio.gather(
            client.chat("First", "events-a", on_event=first.append),
            client.chat("Second", "events-b", on_event=second.append),
        )
        for events in (first, second):
            self.assertEqual([e["type"] for e in events], ["request_start", "model_start", "model_end"])

    async def test_closing_stream_cancels_pending_request(self):
        self.delay = 1
        response = await chat_stream(
            ChatRequest(query="Hello", session_id="cancel-stream"), SimpleNamespace(app=app)
        )
        await anext(response.body_iterator)
        await response.body_iterator.aclose()
        self.assertEqual(self.active, 0)


if __name__ == "__main__":
    unittest.main()
