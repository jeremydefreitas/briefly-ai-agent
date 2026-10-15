"""Test-only JSON-RPC server that fails one tools/call over real stdio."""

import json
import os
import sys

mode = sys.argv[1]
failed_once = False


def reply(request_id, result):
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)


for line in sys.stdin:
    request = json.loads(line)
    if "id" not in request:
        continue
    method = request["method"]
    request_id = request["id"]
    if method == "initialize":
        reply(request_id, {
            "protocolVersion": request["params"]["protocolVersion"],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "fault-test", "version": "1.0.0"},
        })
    elif method == "ping":
        reply(request_id, {})
    elif method == "tools/list":
        reply(request_id, {"tools": [{
            "name": "fault_probe",
            "description": "Get the test service status. May be unavailable.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        }]})
    elif method == "tools/call":
        if not failed_once:
            failed_once = True
            if mode == "disconnect":
                os._exit(0)
            if mode == "invalid-json":
                print("{invalid-json", flush=True)
                continue
            if mode == "invalid-schema":
                reply(request_id, {"content": [{"type": "invalid-content-type"}]})
                continue
            raise ValueError("Unknown fault mode")
        reply(request_id, {"content": [{"type": "text", "text": "FAULT_PROBE_OK"}]})
    else:
        print(json.dumps({"jsonrpc": "2.0", "id": request_id, "error": {
            "code": -32601, "message": "Method not found",
        }}), flush=True)
