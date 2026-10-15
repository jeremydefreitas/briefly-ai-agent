"""Verify real local MCP transports; model responses are mocked."""

import json
import os
import unittest
from unittest.mock import AsyncMock, patch

import httpx2 as httpx
from openai import AsyncOpenAI

import agent_client
import mcp_client
from activity import activity_sink


class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_discovery_invocation_and_directory_boundary(self):
        async with mcp_client.connect_mcp_servers() as servers:
            self.assertEqual({s.name for s in servers}, {"filesystem", "tavily", "open-meteo"})
            filesystem = next(s for s in servers if s.name == "filesystem")
            tavily = next(s for s in servers if s.name == "tavily")
            weather = next(s for s in servers if s.name == "open-meteo")
            weather_tools = await weather.list_tools()
            self.assertEqual({tool.name for tool in weather_tools}, {"geocoding", "weather_forecast"})
            self.assertTrue(all(isinstance(tool.input_schema, dict) for tool in weather_tools))
            invalid_coordinates = await weather.call_tool(
                "weather_forecast", {"latitude": 91, "longitude": 0}
            )
            self.assertTrue(invalid_coordinates.is_error)
            tools = await filesystem.list_tools()
            self.assertIn("read_text_file", {tool.name for tool in tools})
            self.assertNotIn("read_media_file", {tool.name for tool in tools})
            self.assertTrue(all(isinstance(tool.input_schema, dict) for tool in tools))
            self.assertEqual(
                {tool.name for tool in await tavily.list_tools()},
                {"tavily_search", "tavily_extract"},
            )

            result = await filesystem.call_tool(
                "read_text_file", {"path": str(mcp_client.FILES_ROOT / "notes.txt")}
            )
            self.assertFalse(result.is_error)
            self.assertIn("Assignment 1 workspace", result.content[0].text)
            for path in (mcp_client.FILES_ROOT / "missing.txt", mcp_client.PROJECT_ROOT / "main.py"):
                events = []
                token = activity_sink.set(events.append)
                try:
                    result = await filesystem.call_tool("read_text_file", {"path": str(path)})
                finally:
                    activity_sink.reset(token)
                self.assertTrue(result.is_error)
                self.assertEqual([e["type"] for e in events], ["tool_start", "tool_error"])
        self.assertTrue(all(server.session is None for server in servers))

    async def test_sdk_calls_real_mcp_tool_and_receives_result(self):
        calls = []

        def model_response(request):
            payload = json.loads(request.content)
            calls.append(payload)
            tool_messages = [m for m in payload["messages"] if m["role"] == "tool"]
            if tool_messages:
                self.assertIn("Assignment 1 workspace", str(tool_messages[-1]["content"]))
                message = {"role": "assistant", "content": "File read verified."}
                finish_reason = "stop"
            else:
                self.assertIn("read_text_file", {t["function"]["name"] for t in payload["tools"]})
                message = {"role": "assistant", "content": None, "tool_calls": [{
                    "id": "read-notes",
                    "type": "function",
                    "function": {
                        "name": "read_text_file",
                        "arguments": json.dumps({"path": str(mcp_client.FILES_ROOT / "notes.txt")}),
                    },
                }]}
                finish_reason = "tool_calls"
            return httpx.Response(200, json={
                "id": "mock-completion", "object": "chat.completion", "created": 1,
                "model": payload["model"],
                "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
            })

        def create_client(**kwargs):
            return AsyncOpenAI(**kwargs, http_client=httpx.AsyncClient(
                transport=httpx.MockTransport(model_response)
            ))

        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-test-key"}), \
             patch.object(agent_client, "AsyncOpenAI", side_effect=create_client):
            async with mcp_client.connect_mcp_servers() as servers:
                client = agent_client.AgentClient(mcp_servers=servers)
                try:
                    events = []
                    self.assertEqual(await client.chat("Read notes.txt", "mcp-test", on_event=events.append), "File read verified.")
                    self.assertEqual(len(calls), 2)
                    tools = [e for e in events if e["type"].startswith("tool_")]
                    self.assertEqual([e["type"] for e in tools], ["tool_start", "tool_end"])
                    self.assertTrue(all(e["server"] == "filesystem" and e["tool"] == "read_text_file" for e in tools))
                    self.assertTrue(all("arguments" not in e and "result" not in e for e in events))
                    statuses = await client.mcp_status()
                    self.assertTrue(all(s["status"] == "connected" for s in statuses))
                finally:
                    await client.close()

    async def test_unavailable_server_does_not_disable_other_tools(self):
        real_server = mcp_client.ObservedMCPServer
        unavailable = AsyncMock()
        unavailable.connect.side_effect = OSError("Mock transport failure")

        def create_server(**kwargs):
            return unavailable if kwargs["name"] == "tavily" else real_server(**kwargs)

        with patch.object(mcp_client, "ObservedMCPServer", side_effect=create_server):
            with self.assertLogs("mcp_client", level="WARNING"):
                async with mcp_client.connect_mcp_servers() as servers:
                    self.assertEqual({s.name for s in servers}, {"filesystem", "open-meteo"})


if __name__ == "__main__":
    unittest.main()
