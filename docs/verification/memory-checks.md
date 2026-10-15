# Live verification: memory, isolation, and tool-error recovery

Run on 2026-10-12 (America/Los_Angeles); JSON timestamps use UTC.
All five requests shared one application lifespan and exercised the actual
FastAPI POST /chat route through in-process HTTP, live NVIDIA inference, and real
MCP servers. The event wrapper recorded activity without substituting results.

| Check | Session | Observed outcome | Result |
| --- | --- | --- | --- |
| Remember project codename Cedar | verification-memory-a | Acknowledged Cedar; no tools | Passed |
| Recall project codename | verification-memory-a | Answered Cedar; no tools | Passed |
| Ask in a separate session | verification-memory-b | Said it lacked the codename; did not inherit Cedar | Passed |
| Read missing-verification-file.txt | verification-recovery | Real read_text_file error; explained the file does not exist | Passed |
| Read notes.txt after the error | verification-recovery | Real read_text_file succeeded; quoted "Assignment 1 workspace" | Passed |

Every request returned HTTP 200. The missing-file operation was a tool execution
error handled inside the agent loop, rather than an HTTP/service failure. The
successful follow-up verifies that the same conversation continued functioning.

[Full evidence](memory-checks.json) contains exact prompts/responses, session IDs,
connection states, UTC timestamps, tool events, and review assessments.

These checks demonstrate local recall and session isolation while the application
remains running. They do not establish persistence across restart, which the
assignment does not require, or browser/Cloud Run behavior. Controlled transport
interruptions and malformed-response tests remain.
