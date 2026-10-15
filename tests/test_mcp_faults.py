"""Faults cross real MCP stdio; only the external model HTTP is controlled."""

import json
import os
import sys
import unittest
from unittest.mock import patch

import httpx2 as httpx
from openai import AsyncOpenAI

import agent_client
from main import app
from mcp_client import FILES_ROOT, PROJECT_ROOT, ObservedMCPServer, tool_failure


class MCPFaultTests(unittest.IsolatedAsyncioTestCase):
    async def check_fault(self, mode):
        model_inputs = []

        def model_response(request):
            payload = json.loads(request.content)
            model_inputs.append(payload)
            messages = payload["messages"]
            last_user = max(i for i, message in enumerate(messages) if message["role"] == "user")
            recovering = messages[last_user]["content"] == "Read notes.txt"
            results = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
            if results:
                result = str(results[-1]["content"])
                if recovering:
                    self.assertIn("Assignment 1 workspace", result)
                    content = "Assignment 1 workspace"
                else:
                    self.assertIn("The tool failed.", result)
                    self.assertNotIn("FAULT_PROBE_OK", result)
                    content = "The test service status could not be retrieved."
                message = {"role": "assistant", "content": content}
                finish = "stop"
            else:
                name = "read_text_file" if recovering else "fault_probe"
                arguments = {"path": str(FILES_ROOT / "notes.txt")} if recovering else {}
                message = {"role": "assistant", "content": None, "tool_calls": [{
                    "id": f"{mode}-{'recovery' if recovering else 'fault'}",
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments)},
                }]}
                finish = "tool_calls"
            return httpx.Response(200, json={
                "id": "controlled-model", "object": "chat.completion", "created": 1,
                "model": payload["model"],
                "choices": [{"index": 0, "message": message, "finish_reason": finish}],
            })

        def create_client(**kwargs):
            return AsyncOpenAI(**kwargs, http_client=httpx.AsyncClient(
                transport=httpx.MockTransport(model_response)
            ))

        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-test-key"}), \
             patch.object(agent_client, "AsyncOpenAI", side_effect=create_client):
            async with app.router.lifespan_context(app):
                async with ObservedMCPServer(
                    name=f"fault-test-{mode}",
                    params={"command": sys.executable,
                            "args": [str(PROJECT_ROOT / "tests/fixtures/fault_mcp_server.py"), mode],
                            "env": {}},
                    cache_tools_list=True, client_session_timeout_seconds=0.5,
                    failure_error_function=tool_failure,
                ) as faulty:
                    await faulty.list_tools()
                    client = app.state.agent_client
                    client.agent.mcp_servers.append(faulty)
                    original = client.chat
                    events = []

                    async def observe(query, session_id, on_event=None):
                        return await original(query, session_id, on_event=events.append)

                    try:
                        with patch.object(client, "chat", side_effect=observe):
                            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as http:
                                failed_tool = await http.post("/chat", json={"query": "Probe the service", "session_id": mode})
                                self.assertEqual(failed_tool.status_code, 200)
                                self.assertEqual(failed_tool.json()["response"], "The test service status could not be retrieved.")
                                self.assertTrue(any(e["type"] == "tool_error" and e["server"] == faulty.name for e in events))
                                recovery = await http.post("/chat", json={"query": "Read notes.txt", "session_id": mode})
                                self.assertEqual(recovery.status_code, 200)
                                self.assertEqual(recovery.json()["response"], "Assignment 1 workspace")
                                self.assertTrue(any(e["type"] == "tool_end" and e["server"] == "filesystem" for e in events))
                                self.assertEqual(len(model_inputs), 4)
                    finally:
                        client.agent.mcp_servers.remove(faulty)

    async def test_transport_disconnect_and_recovery(self):
        await self.check_fault("disconnect")

    async def test_invalid_json_and_recovery(self):
        await self.check_fault("invalid-json")

    async def test_invalid_schema_and_recovery(self):
        await self.check_fault("invalid-schema")


if __name__ == "__main__":
    unittest.main()
