"""Connect installed MCP servers for the application's lifetime."""

import json
import logging
import os
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from agents.mcp import MCPServerStdio

from activity import emit_activity

PROJECT_ROOT = Path(__file__).resolve().parent
FILES_ROOT = PROJECT_ROOT / "data"
logger = logging.getLogger(__name__)


def tool_failure(_context, _error) -> str:
    return "The tool failed. Explain the failure without inventing a result."


class ObservedMCPServer(MCPServerStdio):
    async def call_tool(self, tool_name, arguments, meta=None):
        details = {"server": self.name, "tool": tool_name}
        emit_activity("tool_start", f"{self.name}: running {tool_name}.", **details)
        try:
            result = await super().call_tool(tool_name, arguments, meta)
        except Exception:
            emit_activity("tool_error", f"{self.name}: {tool_name} failed.", **details)
            raise
        if result.is_error:
            emit_activity("tool_error", f"{self.name}: {tool_name} returned an error.", **details)
        else:
            emit_activity("tool_end", f"{self.name}: {tool_name} completed.", **details)
        return result


def load_server_configs() -> dict:
    config_path = PROJECT_ROOT / (os.environ.get("MCP_SERVERS_CONFIG") or "mcp_servers.json")
    return json.loads(config_path.read_text())["mcpServers"]


@asynccontextmanager
async def connect_mcp_servers():
    configs = load_server_configs()
    FILES_ROOT.mkdir(exist_ok=True)
    servers = []

    async with AsyncExitStack() as stack:
        for name, config in configs.items():
            server = ObservedMCPServer(
                name=name,
                params={
                    "command": config["command"],
                    "args": [str(PROJECT_ROOT / arg) for arg in config["args"]],
                    # Keep server dotenv loading away from application credentials.
                    "cwd": str(FILES_ROOT),
                    "env": {key: os.environ.get(key, "") for key in config.get("env", [])},
                },
                cache_tools_list=True,
                client_session_timeout_seconds=30,
                tool_filter=config.get("tool_filter"),
                failure_error_function=tool_failure,
            )
            try:
                await server.connect()
                stack.push_async_callback(server.cleanup)
                tools = await server.list_tools()
            except Exception as error:
                logger.warning("MCP server %s unavailable (%s).", name, type(error).__name__)
                continue
            servers.append(server)
            logger.info("Connected MCP server %s with %d tools.", name, len(tools))
        yield servers
