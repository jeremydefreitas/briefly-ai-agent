# Process log — CSCI 599 Assignment 1

Current deployment: [csci599-a1](https://csci599-a1-2ez6etscva-uw.a.run.app).
This log combines an AI-assisted factual development account with the existing
personal reflection. Detailed dated entries are preserved in
[development history](docs/development-history.md).

## AI tools used

- Codex desktop assistant (GPT-6-based; exact serving build not available) for
  code generation, debugging, verification, deployment tooling, and documentation.
- NVIDIA NIM Nemotron 3.5 Lightning and Nemotron 3 Ultra as runtime models during
  integration/live verification. The deployed model is
  `nvidia/nemotron-3-ultra-550b-a55b`.

## Development narrative

Development began with a Python virtual environment, pinned dependencies, an ignored .env file, and prompts.md. The initial instruction was “Set up the workspace.” The configuration uses NVIDIA NIM while keeping the OpenAI-compatible environment variable names.

The next stage added a reusable asynchronous client, the Agents SDK runner, and FastAPI's /chat endpoint. Framework-native SQLiteSession objects supplied conversation history keyed by session_id, with locks to serialize turns within a session. Filesystem and Tavily MCP servers were integrated through real stdio discovery and invocation. Tests then checked direct answers, actual file reads, search-and-save workflows, memory isolation, and tool failures.

Open-Meteo was added as the third server. Its initial npx configuration exposed an argument-path incompatibility, so the server was pinned locally and launched through Node. The prompt: "create a simple UI on the the apps root that allows for interacting with the agent through the frontend" started the development of a frontend for the application, so that this assignment can be used beyond this coursework. The frontend developed into Briefly, a useful briefing genterator tool. Feeding debug logs to Codex led to reproducing NVIDIA server errors and timeouts, adding bounded model-call retries, and limiting briefing research.

Packaging used a multi-stage, non-root Docker image. Container tests exposed a hard-coded interpreter path in a test fixture; switching to sys.executable made the suite portable. Finally, the image was pushed to Artifact Registry and deployed to Cloud Run with Secret Manager references. Public verification exercised all three MCPs, session memory, multi-step research, and recovery. The previously inconclusive malformed-JSON check passed on a separate live local rerun.

## Verification narrative

Verification went beyond one successful prompt. The 23 Python tests exercise the
actual FastAPI routes, SDK runner/session memory, real stdio MCP subprocesses,
schemas, directory boundaries, concurrency, cancellation, model retries, and
fault handling; external model HTTP is mocked in those deterministic tests.
Node checks cover stream decoding, UI events, exports, safe Markdown formatting,
and weather sections using a minimal DOM. They do not establish browser layout.
Both suites also passed inside the non-root Linux container. pip check passed.

Separate live checks used NVIDIA inference and real MCP tools without mocked
responses. On Cloud Run, all three connections were healthy, the required /chat
contract worked, no-tool arithmetic avoided tools, geocoding preceded weather,
search/extraction preceded file creation, the saved file was read back, memory
recall/isolation passed, and a missing-file failure was followed by a successful
read in the same session. The two saved source URLs were independently opened.
An isolated local fault server tested transport and schema failures; a final
live invalid-JSON rerun explained the failure and recovered.

The final model comparison found Lightning skipped tool-dependent requests;
Ultra completed actual file, weather, and search calls, so the deployed model
and defaults use Ultra. The final assignment-named service passed public UI,
MCP connectivity, arithmetic, and filesystem checks.

The final submission run repeated nine behavioral checks on the current URL; all
passed, including memory, all three MCPs, multi-step work, and error recovery.
Transient provider errors recovered through the existing bounded retries.

Evidence: [final submission review](docs/verification/submission-review.md),
[current deployment](docs/verification/assignment-exact-url.md),
[model comparison](docs/verification/model-tool-comparison.md),
[final cloud report](docs/verification/cloud-final-checks.md),
[deployment checks](docs/verification/cloud-smoke-checks.md),
[container checks](docs/verification/docker-checks.md),
[fault coverage](docs/verification/fault-checks.md), and
[complete dated history](docs/development-history.md).

## What I learned

In this project I used Codex mainly as a coding agent and QA tester. I heavily controlled the architecture
and development planning which allowed me to retain my understanding of the implementations without manually 
writing each line. With this structure, the development flow was smooth and prevented Codex from hitting any walls. 

## Prompts and attribution

[Instructional prompts](prompts.md) preserve substantive user prompts by date.
The development narrative includes short examples; the complete wording is in
that log. Official SDK, MCP, Google Cloud, and Docker documentation informed the
implementation. No external tutorial application code is claimed as copied or
substantially adapted. The external filesystem, Tavily, and Open-Meteo servers
are attributed individually in README. The detailed history records documentation
consulted and actual verification outcomes.
