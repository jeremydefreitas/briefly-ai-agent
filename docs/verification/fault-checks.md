# Verification: MCP transport and malformed responses

Run on 2026-10-12 (America/Los_Angeles). Faults are produced by a test-only
JSON-RPC subprocess, not by altering the production filesystem/Tavily servers.
The fixture is not configured in the production manifest and does not count as a
third integrated server for rubric credit.

| Injected fault | Controlled /chat result | Follow-up in same session |
| --- | --- | --- |
| Server exits during tools/call | Passed: tool_error, safe failure explanation | HTTP 200; real filesystem read succeeded |
| Invalid JSON over stdio | Passed: parser rejects input, bounded tool failure, safe explanation | HTTP 200; real filesystem read succeeded |
| Valid JSON with invalid content schema | Passed: schema rejected, tool_error, safe explanation | HTTP 200; real filesystem read succeeded |

The controlled tests use the actual SDK runner, /chat route, and real MCP stdio
transports. External model HTTP is mocked to make protocol tests deterministic.
Assertions check that the sanitized failure reaches the model and no successful
fault-probe result is invented. They do not demonstrate a live model's reasoning.
Expected parser/error diagnostics appear in test logs without crashing the app.

## Live model checks and caveat

Live NVIDIA checks passed for the disconnect and invalid-schema faults. Both
were followed by successful real filesystem reads in the same session.

The initial invalid-JSON call emitted tool_error but returned a safe HTTP 502,
and its follow-up also returned 502. A diagnostic retry encountered an upstream
NVIDIA HTTP 500 before invoking the fault tool, then completed its filesystem
follow-up. Therefore the live invalid-JSON result is **inconclusive**, even though
its deterministic protocol/recovery test passed. No backend session corruption
was established, and no production code fix was made on that assumption.

## Final live malformed-JSON rerun (2026-10-14)

The previously inconclusive invalid-JSON case was rerun using live NVIDIA
Nemotron 3 Ultra through the actual local /chat route and the isolated real
stdio fault server. The SDK emitted a tool_error, the model returned HTTP 200
explaining it could not retrieve the status, and a follow-up in that same session
successfully read notes.txt with HTTP 200. See fault-checks-final-live.json.
The initial provider failures remain in their original records. This resolves
the local live caveat; malformed responses were not injected into public Cloud Run.

## Evidence and regression

- [Controlled outcomes](fault-checks.json)
- [Initial live responses/events](fault-checks-initial.json)
- [Live provider diagnostic retry](fault-checks-provider-retry.json)
- Reusable tests: `tests/test_mcp_faults.py`
- Test-only server: `tests/fixtures/fault_mcp_server.py`

All 20 Python tests passed, as did frontend stream checks and compilation.
Recovery here means the application can perform another valid request using a
healthy MCP server. Automatic reconnection/restart of the exited test server was
not tested or implemented. Cloud Run behavior remains to be checked after deployment.
