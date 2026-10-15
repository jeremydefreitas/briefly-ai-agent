# Live verification: no-tool answer and filesystem use

Run on 2026-10-12 (America/Los_Angeles); timestamps in the JSON evidence use UTC.

These checks exercised the actual FastAPI `POST /chat` route through an in-process
HTTP transport, with live NVIDIA inference and real MCP subprocesses. The HTTP
callback wrapper recorded operational events without replacing model or tool
responses. This is local backend verification, not browser or Cloud Run testing.
Both filesystem and Tavily MCP connections responded to health checks before the run.

## No-tool answer: passed

Prompt: `What is 12 × 8?`

Session: `verification-no-tool`. HTTP status: 200.

Actual response: `12 × 8 = 96`.

One model call and zero MCP calls were observed. The answer was correct, and the
agent did not force tool use for a simple arithmetic question.

## Filesystem use: passed

Prompt: `Read notes.txt and summarize it.`

Session: `verification-filesystem`. HTTP status: 200.

Actual response:

> The file `notes.txt` contains a brief note indicating that this folder serves as the working directory for the filesystem MCP server. It can read and write files here, while application code and credentials are stored outside this directory.

Observed sequence: model request/response, filesystem `read_text_file` start and
successful completion, then a second model request/response for the final answer.
The summary accurately reflects `data/notes.txt`; no tool errors were observed.

Full responses, timestamps, connection states, tool events, and the source-file
snapshot are in [core-checks.json](core-checks.json).

Remaining live checks: Tavily selection, multi-tool workflow, memory recall,
session isolation, and recovery after a tool failure.
