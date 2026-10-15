# Process log - working notes

These are factual setup notes, not the final submission narrative. The student
should write the required 200-300 word development narrative and personal learning
reflection in their own voice as the project progresses.

## AI tools used

- Codex desktop assistant (GPT-6-based) for repository setup and SDK integration.
- Model backend for checks: configured by `OPENAI_MODEL`. Initial OpenAI request returned HTTP 429; the user later reported a successful NVIDIA NIM connection check.

## 2026-10-12 - Initial setup

- Read the assignment PDF and confirmed the chosen OpenAI Agents SDK path is supported.
- Inspected the workspace: an empty Git repository already existed.
- Selected Python 3.13 and a project-local virtual environment.
- Added environment templates, Git exclusions, a real Agents SDK smoke-check script,
  setup instructions, and the instructional prompt log in `prompts.md`.
- Consulted the official SDK quickstart:
  https://developers.openai.com/api/docs/guides/agents/quickstart
- Live API verification requires the user's key. No key was present in the initial shell environment.

## Verification

- Installed `openai-agents==0.23.1`, `openai==3.29.0`, and
  `python-dotenv==1.2.4` into `.venv`; froze all installed dependencies into
  `requirements.txt`. The first download attempt failed on sandbox DNS; the
  approved network retry succeeded.
- `pip check`: passed, no broken requirements.
- Python compilation and SDK agent/configuration construction: passed.
- `git check-ignore`: confirmed `.env` and `.venv` are excluded.
- Ran `scripts/check_openai.py`: exited with code 2 and a clear missing-key
  message. No API request was sent, and key validity is still unverified.

## Student reflection (complete later)

Describe what you personally learned, decisions you made, and what required your
own investigation. Do not present generated reflections as personal experience.

## 2026-10-12 - Assignment and workspace review

- Extracted and reviewed text from all 12 PDF pages using Python standard-library PDF stream and embedded character-map decoding. Poppler was unavailable; Swift failed on restricted compiler-cache access and the approval retry was cancelled; PDFKit document loading also failed. Visual PDF review was not completed. No dependencies were installed for this review.
- Confirmed the root and docs copies of the assignment PDF are byte-identical.
- Re-ran pip check: no broken requirements. Confirmed requirements.txt matches pip freeze.
- Confirmed Git has no commits yet and the project files are untracked. Local .env and .venv exist; credential values were not displayed.
- Reviewed the smoke-check script and prior missing-key verification record. No new API request was sent, so successful API access remains unverified by this review.
- Confirmed that the HTTP service, MCP server integrations, SDK session memory, Docker packaging, Cloud Run deployment, and required diagrams remain future milestones.

## 2026-10-12 - API smoke check with configured key

- User confirmed retaining Python and adding an API key to local .env.
- Ran .venv/bin/python scripts/check_openai.py. The sandboxed attempt exited 1 with a connection failure.
- Retried the same script with approved network access. OpenAI returned HTTP 429; the script exited 1. No model response completed.
- The script groups quota, billing, and rate-limit errors together, so this result does not establish the specific cause or prove the key is invalid. Successful model access remains unverified. Credential values were not displayed or copied into documentation.

## 2026-10-12 - NVIDIA NIM backend configuration

- Retained Python and the OpenAI Agents SDK. Changed the smoke check to an explicit OpenAIChatCompletionsModel backed by NVIDIA's OpenAI-compatible endpoint, https://integrate.api.nvidia.com/v1. Default model: nvidia/nemotron-3.5-lightning-30b-a3b (Nemotron 3.5 Lightning, listed in the assignment).
- Final provider configuration uses NVIDIA_API_KEY, NVIDIA_BASE_URL, and NVIDIA_MODEL. Removed the previous key from local .env and left NVIDIA_API_KEY blank for the user. No provider-specific key-format check was added. Local .env remains ignored and mode 0600; credential values were not displayed or copied into documentation.
- Renamed scripts/check_openai.py to scripts/check_nvidia.py and updated the environment template and README. SDK tracing stays disabled; thinking is disabled for the short connection check. No dependency changes were needed.
- Consulted official provider and model documentation:
  - https://developers.openai.com/api/docs/guides/agents/models
  - https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b
  - https://docs.nvidia.com/nemo/datadesigner/concepts/models/default-model-settings
- Verification: Python compilation passed. Eight local mocked HTTP checks passed through the real SDK Runner and Chat Completions adapter: missing key, old OpenAI variables only, successful completion, HTTP 401/429/500, connection failure, and timeout. Verified the NVIDIA request URL/model, token limit, and thinking setting. These were mocked requests, not live API successes.
- Running the final script with the local configuration exited 2 with the NVIDIA key setup message. No live NVIDIA request was sent. Live verification remains pending the NVIDIA key.

## 2026-10-12 - Restore OpenAI-compatible variable names

- At the user's request, changed the final configuration to OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL in scripts/check_nvidia.py, .env.example, README.md, and local .env. Existing local values were preserved without displaying credentials. This supersedes the prior NVIDIA_* naming decision.
- Kept the NVIDIA endpoint, Nemotron 3.5 Lightning default, explicit OpenAIChatCompletionsModel adapter, and disabled tracing. No dependency changes.
- Verification: compilation passed; mocked SDK completion passed using OPENAI_* values and verified the NVIDIA Chat Completions URL, model, and dummy authorization value. Missing-key check stopped before making a request. Local .env names and non-secret endpoint/model were checked successfully without displaying credentials.
- No live API request was made during this change.

## 2026-10-12 - Reusable client and POST /chat

- User reported the NVIDIA NIM connection check worked. This is user-reported evidence; no live request was performed by the assistant during this milestone.
- Removed scripts/check_nvidia.py as requested. Added agent_client.py with a reusable AsyncOpenAI client, explicit Chat Completions model adapter, and SDK SQLiteSession memory. The session registry stores SDK sessions and per-session locks. Turns in a conversation are serialized; distinct sessions can run concurrently.
- Added main.py with FastAPI lifespan startup/shutdown, validated POST /chat requests containing query and session_id, response bodies containing response, and PORT-aware Uvicorn startup. Missing credentials fail at startup. Timeouts, connection errors, rate limits, API errors, and malformed/empty model replies receive short HTTP errors without exposing provider payloads.
- Installed fastapi==0.143.0 and annotated-doc==0.0.5. Initial sandbox download failed on DNS; approved network retry succeeded. Added FastAPI and Uvicorn to direct dependencies and refreshed requirements.txt from installed versions.
- Updated README with run instructions, curl examples, implementation/memory limits, remaining milestones, costs, and test instructions. Added local PORT default to .env.example.
- Verification: all seven unittest integration tests passed. They used the real SDK Runner, SQLiteSession, and FastAPI route with mocked model HTTP responses. Checked response schema, same-session history including prior assistant reply, session isolation, invalid inputs without model calls, HTTP 401/429/500, timeout, connection failure, malformed/empty replies, per-session ordering, different-session concurrency, missing-key startup, and shutdown client cleanup. These tests establish memory replay, not a live model's semantic recall.
- pip check passed and Python compilation passed. No MCP servers or deployment were implemented in this milestone.
- Consulted official SDK sessions and FastAPI request/lifespan documentation linked in README. No tutorial code was copied or substantially adapted.

## 2026-10-12 - Root chat UI

- Added static/index.html and GET / serving the page through FastAPI FileResponse. No frontend dependencies were installed.
- The UI calls the existing POST /chat endpoint, reuses a generated session ID across follow-ups, and creates a fresh ID on New chat or page reload. Includes responsive styling, labelled inputs, keyboard submission, pending feedback, duplicate-submission prevention, and error messages with the query restored for retry. Replies are rendered through textContent as plain text.
- Updated README and logged the user prompt.
- Verification: an in-process HTTP check confirmed GET / returns status 200, HTML content type, and the expected file; /chat remains in the API schema. Frontend JavaScript syntax passed Node's VM parser. All seven existing mocked HTTP/SDK integration tests passed. No live model request was sent, and browser interaction/visual rendering was not verified in this milestone.

## 2026-10-12 - Filesystem and Tavily MCP integration

- Installed @modelcontextprotocol/server-filesystem==1.0.0 and tavily-mcp==0.2.22 as project-local Node dependencies with exact direct version pins and package-lock.json. Node.js v22.14.0 was already available. Initial sandbox download failed on DNS; the approved network retry succeeded. Python dependencies were unchanged.
- The initial npm audit reported an advisory in Tavily's pinned MCP TypeScript SDK. Added a scoped override to @modelcontextprotocol/sdk==1.31.0; reinstall reported zero vulnerabilities. The local transport/tool tests passed with this override. Advisory: https://github.com/advisories/GHSA-6qxp-vccf-f47h.
- Added mcp_servers.json and mcp_client.py. FastAPI lifespan connects both local stdio servers, performs real tools/list discovery, caches tool schemas, attaches connected servers to the SDK agent, and closes them at shutdown. Failed server connections/discovery are logged by name and exception type; other servers remain available. No credential values are placed in the manifest or printed.
- Restricted filesystem access to data/ and added data/notes.txt for verification. Blocked media reads for the text-only model. Exposed only Tavily search/extract. Server subprocesses run in data/ and receive declared environment variables rather than the application's full credential environment.
- TAVILY_API_KEY was unset during verification. The installed Tavily server supports limited keyless search/extract, so both servers can be connected without it. The user may add the key locally and restart to use account limits.
- Updated the SDK agent's instructions to use file tools, web search/extraction, source URLs, and multiple calls when needed. No keyword routing or simulated production tool responses were added. Added safe route handling for MCP protocol/schema exceptions and a sanitized SDK tool failure message.
- Real MCP verification: tools/list discovered 13 filtered filesystem tools and 2 filtered Tavily tools. Filesystem tools/call read data/notes.txt successfully. The sandbox Tavily search returned an error; an approved network retry reached Tavily. The initial verification harness incorrectly assumed JSON text and failed to parse the formatted result; it was corrected. The final strict check verified five actual search result entries with source URLs via tavily_search. No Tavily key was used.
- Live agent verification: POST /chat returned HTTP 200, NVIDIA selected and made one real filesystem MCP call, and its answer contained the sample file's first line. This was a real NVIDIA model request with real tool invocation, not a mocked model run. Live Tavily selection by the model and multi-step tool chaining remain to be verified.
- Final verification: all 11 unittest tests passed. Existing HTTP/session tests use a mocked model and MCP-free test lifespan; MCP tests launch the real installed servers and test discovery, declared schemas, reading, denied paths outside data/, missing files, cleanup, partial server unavailability, and a real MCP call in a mocked model loop. HTTP tests cover mocked MCP protocol/schema discovery errors. An initial discovery-error test used an unnamed AsyncMock where the SDK expected a string name; fixing the test fixture resolved both test errors.
- pip check and Python compilation passed. Updated README with npm ci, manifest details, examples, server attribution, costs, and remaining assignment milestones. Consulted the official OpenAI SDK MCP guidance and each server's official repository. No tutorial code was copied or substantially adapted.

## 2026-10-12 - MCP status and live chat activity

- Added GET /mcp/status with actual MCP ping checks (three-second deadlines), exposed tool counts, unavailable configured server states, and Tavily's keyless/authenticated configuration mode. Connected means transport connectivity, not external provider quota or credential validity.
- Added request-scoped activity callbacks with ContextVar, SDK model-call hooks, and an observed MCP server wrapper emitting real tools/call start/completion/failure events. The wrapper checks the MCP error flag and distinguishes a tool error from successful completion. Activity contains names/states and timestamps, without arguments, raw results, credentials, or private reasoning.
- Added POST /chat/stream using newline-delimited JSON, a request-local event queue, heartbeats, safe streamed errors, final response events, and cancellation of pending work on disconnect. Retained the assignment's JSON POST /chat endpoint. Shared error mapping serves both routes.
- Updated the frontend with MCP badges, active tool highlighting, a collapsible timestamped activity panel, 10-second status polling, incremental UTF-8/JSON stream parsing, and error/retry handling. UI logs are bounded to 200 entries and cleared on New chat. No dependencies were added.
- Verification: all 17 Python tests passed, including real filesystem/Tavily MCP subprocess health checks, real filesystem tool events in a mocked model loop, tool-error flags, early stream delivery before final completion, per-request event isolation, safe provider errors, and stream cancellation. No live external model/search request was sent during this milestone.
- Node frontend checks passed for connection/unavailable badges, active tool and activity updates before final completion, JSON messages split across chunks, multibyte UTF-8 decoding, and streamed error handling. They use a minimal DOM rather than a real browser; visual layout and actual browser interaction were not verified. Python compilation passed.
- Updated README and instructional prompt log. Consulted official SDK running-agents guidance and inspected installed RunHooks and MCP ping interfaces. No tutorial code was copied or substantially adapted.

## 2026-10-12 - Progress audit

- Reviewed current source inventory, README, server manifest, recorded verification, and Git status against the previously read assignment requirements.
- Confirmed two configured MCP servers and existing HTTP/session/UI/activity code. No Dockerfile, .dockerignore, deploy.sh, required architecture diagrams, submission ZIP, or recorded live Cloud Run deployment is present. Git still has no tracked project files/commits.
- Outstanding verification includes live model recall and isolation, Tavily selection by the model, no-tool queries, multi-step tool chains, and broader transport/malformed-response failure checks. Previously recorded tests and live checks were not rerun during this audit.
- Final student-written development narrative and personal learning reflection remain incomplete. A third server is needed for full additional-server rubric credit, while two satisfy the minimum server count.

## 2026-10-12 - Live no-tool and filesystem verification

- Ran the first two planned behavior checks through the actual POST /chat route with an in-process HTTP transport, live NVIDIA inference, and real filesystem/Tavily MCP subprocesses. An approved network execution enabled the live model requests. The callback wrapper only recorded events; it did not mock or substitute model/tool responses. Both MCP connections responded to health checks before the run.
- No-tool check passed: "What is 12 × 8?" returned HTTP 200 and "12 × 8 = 96". Observed one model call and zero MCP tool calls, with both servers available.
- Filesystem check passed: "Read notes.txt and summarize it." returned HTTP 200. Observed one real filesystem read_text_file call with a successful completion, followed by a second model call for synthesis. Reviewed the response against data/notes.txt; it accurately describes the directory, read/write access, and separation from code/credentials. No tool error was observed.
- Saved exact responses, UTC timestamps, connection states, tool events, assessments, and the public sample-file snapshot in docs/verification/core-checks.json; readable report in docs/verification/core-checks.md. No credential values were displayed or recorded.
- These are local backend checks; browser interaction and Cloud Run behavior were not tested. Tavily selection, multi-step calls, live memory/isolation, and tool-failure recovery remain for subsequent verification steps. No production code or dependencies changed, so the automated suite was not rerun.

## 2026-10-12 - Live Tavily selection and multi-step verification

- Ran two live POST /chat checks using in-process HTTP requests, live NVIDIA inference, real MCP servers, and an event-recording wrapper that did not mock responses. Both MCP servers responded to health checks; Tavily used keyless mode. Approved network access enabled the requests.
- Tavily selection passed: "Search for official MCP documentation and cite sources." returned HTTP 200. Observed successful tavily_search followed by model synthesis with relevant official documentation links.
- Multi-step workflow passed: "Search for official MCP documentation, then save a short summary and source URLs to verification-summary.txt." returned HTTP 200. Observed tavily_search, another model step, successful filesystem write_file, and final synthesis.
- Independently read data/verification-summary.txt and compared it with the evidence snapshot. It exists and contains a substantive MCP summary with source URLs. No tool errors occurred.
- Source review found a quality caveat: the saved file grouped an alternative documentation mirror under Official Sources. The official versioned specification and getting-started URLs opened successfully; a separately cited SDK URL was inaccessible through the review browser, so its validity is inconclusive. The workflow checks passed, but the responses were not certified as entirely factually/citationally correct. Source-labeling improvements remain.
- Saved exact prompts, responses, operational events, assessments, source-check outcomes, and a saved-file snapshot in docs/verification/search-checks.json; readable report in docs/verification/search-checks.md. Credentials were not displayed or recorded. No production code/dependencies changed.
- Memory recall, session isolation, and tool-error recovery remain for the next live verification step. These checks do not establish browser or Cloud Run behavior.

## 2026-10-12 - Live memory, isolation, and tool-error recovery

- Ran five real POST /chat requests in one application lifespan using live NVIDIA inference and real MCP servers through in-process HTTP. Approved network access enabled model calls. The callback wrapper recorded events without substituting model/tool responses.
- Memory setup/recall passed: session verification-memory-a acknowledged project codename Cedar and recalled it in the next turn, with no MCP calls.
- Isolation passed: a new session verification-memory-b did not inherit Cedar and explicitly stated it lacked the codename.
- Missing-file handling passed: the model selected real filesystem read_text_file for missing-verification-file.txt; the tool returned an error and the agent reported that the file did not exist. No file content was invented.
- Recovery passed: in that same verification-recovery session, a subsequent read_text_file succeeded for notes.txt and the response correctly quoted "Assignment 1 workspace". All five HTTP responses were 200; the tool execution error was handled inside the agent loop.
- Recorded exact prompts/responses, session IDs, UTC timestamps, operational events, and passed assessments in docs/verification/memory-checks.json, with a readable report in docs/verification/memory-checks.md. No credentials were displayed or recorded.
- These checks cover local live memory and execution-error recovery, not restart durability, browser rendering, or Cloud Run. Transport interruption and malformed-response fault injection, plus the previously identified citation-quality issue, remain. Production code and dependencies were unchanged; automated tests were not rerun.

## 2026-10-12 - MCP transport and malformed-response fault injection

- Added a test-only stdio JSON-RPC fixture with three first-call faults: exit during tools/call, invalid JSON, and valid JSON carrying an invalid content schema. It is never configured in production and does not count toward the third-server rubric requirement. Normal server processes/configuration were not changed.
- Initial live NVIDIA /chat runs passed disconnect and invalid-schema handling, with actual tool_error events, clear failure explanations, and successful real filesystem reads in the same sessions afterward.
- Initial live invalid-JSON run produced tool_error but returned a safe HTTP 502; its follow-up also returned 502. A diagnostic retry produced NVIDIA HTTP 500 (Internal server error) before the fault tool was invoked, then completed the filesystem recovery request. Live invalid-JSON verification is inconclusive; attribution to poisoned session memory or a backend bug was not established. No speculative production fix was made. Sanitized provider error details contain no keys.
- Added three deterministic integration tests using real MCP stdio/server faults, the SDK runner, and actual /chat route with external model HTTP mocked. All three passed: SDK rejected/handled each fault, delivered the sanitized failure to the controlled model, emitted tool_error, and completed a real filesystem read in the same session after the error. Invalid JSON was bounded by the test server's 0.5-second client timeout. These tests establish protocol/application behavior, not live semantic reasoning.
- Full regression passed: 20 Python tests; Node frontend stream/status checks; fixture/test compilation. SDK parser diagnostics for deliberately malformed input were expected. Production dependencies/code were unchanged.
- Evidence: docs/verification/fault-checks.md and fault-checks.json (controlled outcomes), fault-checks-initial.json (original live results), and fault-checks-provider-retry.json (diagnostic retry). No credential values were displayed or saved.
- No automatic reconnection of an exited MCP server was verified. Cloud Run behavior and a conclusive live invalid-JSON rerun remain; source-labeling improvement also remains from prior verification.

## 2026-10-13 - Open-Meteo review

- Found user-added open-meteo manifest entry using npx with -y/-p and the open-meteo-mcp-server package, plus an agent instruction to use Open-Meteo for weather.
- Confirmed the manifest command matches the server's official README. Identified a loader incompatibility: mcp_client.py prefixes every argument with PROJECT_ROOT, turning npx flags and package names into filesystem paths. Printed expanded non-secret arguments to confirm this without launching or installing the server.
- Open-Meteo is absent from package.json/package-lock.json and the project-local node_modules. Dynamic npx installation is possible once argument handling is fixed; a pinned local install with a Node entry point would match existing deployment conventions.
- Ran only test_status_reports_missing_servers: failed because it still asserts exactly filesystem/tavily, while the manifest now has open-meteo as well. test_mcp.py also contains a two-server expectation, but was not run in this review.
- Server discovery, weather invocation, live agent selection, tests, and README attribution/rationale remain to be completed. The current server docs require Node >=22; local Node is already v22.14.0, while the project's README still lists >=20. No Open-Meteo API key is required for the documented local non-commercial usage.
- Consulted https://github.com/cmer81/open-meteo-mcp/blob/main/README.md. No production code or dependencies were changed, and no Open-Meteo/weather/model request was sent.

## 2026-10-13 - Complete and verify Open-Meteo

- At the start of execution, the user had added open-meteo-mcp-server with a ^2.5.2 dependency. Ran npm install --save-exact to pin it to 2.5.2 with the lockfile. Sandbox registry resolution failed; the approved network retry reported the install up to date and zero vulnerabilities. Python dependencies were unchanged.
- Replaced the incompatible npx manifest entry with node plus the installed node_modules/open-meteo-mcp-server/dist/index.js path. This matches the existing loader's path arguments and avoids startup package downloads. Filtered the server to geocoding and weather_forecast for the basic workflow. Preserved and expanded the user's weather instruction to resolve place names first and include units/local time. No new keys were required.
- Updated two-server expectations to include Open-Meteo and verified tool schemas. Added a real MCP invalid-coordinate check that fails validation locally. The unavailable-Tavily test now retains filesystem and weather. Updated the frontend test fixture to verify a third badge; production frontend already supports dynamically named servers.
- Live verification passed: all three MCP connections responded to ping; Open-Meteo discovered two exposed tools; actual geocoding and forecast calls returned Los Angeles coordinates/weather. A real NVIDIA /chat request returned HTTP 200 and selected geocoding followed by weather_forecast. Captured tool arguments confirm it passed the resolved coordinates. The response temperature, Fahrenheit units, and local time match the API result. Wrappers recorded events/results without substituting responses.
- Saved actual schemas, prompts, responses, event timestamps, arguments, weather results, and reviewed pass outcomes in docs/verification/open-meteo-checks.json; readable report in open-meteo-checks.md. These are local backend checks, not browser/Cloud Run verification. Credentials were not displayed or copied.
- Final regression: all 20 Python tests passed; Node frontend stream/status checks passed; pip check passed. Updated README Node requirement to >=22, third-server attribution/rationale, tool scope, sample query, and remaining milestones.
- Consulted the chosen server's official README and package manifest; no tutorial code was copied or substantially adapted. Open-Meteo is the third configured production MCP server, distinct from the test-only fault fixture.

## 2026-10-13 - Briefly briefing frontend

- Redesigned static/index.html as an editorial briefing workspace with a guided setup panel, explanatory three-step guide, politics/technology/weather examples, report reader, follow-up composer, research connection badges, and live activity. Responsive CSS adapts the two-column desktop layout to a stacked mobile layout.
- Added briefing types, timeframe, region/location, focus, and reading-length inputs. Frontend requests include the browser's current timestamp/timezone, source recency and primary-source guidance, a structured briefing outline, uncertainty handling, and no automatic file saving. Weather requests ask for geocoding/forecasts; empty custom topics or weather locations are rejected before submission. These are request instructions, not guarantees of model compliance.
- Added safe DOM-based rendering of headings, lists, tables, bold/code text, and HTTP/HTTPS source links. Model HTML is treated as text, and non-HTTP link protocols are not activated. Added copy/plain-text download of the latest response and an explicit workspace-save request through the existing agent. Follow-ups retain the session; New workspace clears UI state and creates a fresh session.
- Production changes are confined to the frontend. /chat JSON contract, /chat/stream protocol, SDK client/memory, and MCP implementation are unchanged. No dependencies were added. Updated README and instructional prompt log. Source-quality guidance is added to briefing requests; the previously recorded general-agent citation issue is not claimed universally fixed.
- Verification: all 20 Python tests passed. Expanded Node frontend checks passed for existing stream/status behavior, briefing scope/date/tool/source guidance, safe formatted rendering (including attempted HTML/javascript links), generation through the existing stream API, follow-up/reset IDs, copy/download text preservation, explicit filesystem-save requests, guided form metadata, and custom-topic validation. In-process GET / served the redesigned page with HTTP 200; both assignment chat endpoints remain in the API schema.
- Attempted browser inspection through computer-use tooling; no browser was available. Visual layout and native clipboard/download behavior were not browser-verified. Node checks use a minimal DOM and simulated responses. No live briefing/model/search request was sent during this milestone, and no credentials were displayed or recorded.


## 2026-10-13 - Briefing failure recovery

- Reproduced the frontend's default Global politics / Today / Global / standard prompt with the real SDK client, NVIDIA NIM, and all three MCP servers. Discovery succeeded, Tavily search completed, and the next model call returned NVIDIA HTTP 500 with an internal-server-error body. This failure occurred in the provider call after research, not during frontend rendering.
- Added SDK runner-managed retries (two retries after the initial call) for model HTTP 500/502/503/504, connection failures, and timeouts. The retries target the individual model request, preserving completed tool results. Retrying emits request-scoped model_retry activity, and exhausted HTTP server failures now have a specific safe message. Credentials and provider response details are not sent to the browser.
- Tightened the frontend briefing instruction to make at most three search calls with five results each, exclude raw search page content, and make at most one extraction call for up to two pages only if excerpts are insufficient; then draft with research gaps disclosed. This is model guidance, not an enforced payload limit. No model, keys, dependencies, assignment routes, or session mechanism were changed.
- An initial live rerun completed search and extraction but timed out on final inference. A subsequent live run demonstrated a model_retry event after a timeout; final outcome recorded below when available. Bounded retries improve recovery but do not guarantee NVIDIA availability.
- Node frontend checks passed. Python regression results and final live outcome are recorded below. Consulted official OpenAI models/provider documentation and verified retry semantics against the installed Python SDK implementation.
- Final regression: all 23 Python tests passed (17.877 seconds), including recovery after a completed tool without replaying that tool, identical payload reuse, two-retry exhaustion, transient timeout recovery, and no authentication-error retry. Node frontend checks passed, including research-budget prompt assertions.
- Final live verification of the updated prompt succeeded: real NVIDIA inference selected three Tavily searches and one extraction, then returned a nonempty 5,659-character briefing. Request activity began at 09:46:09.853 UTC and final model response arrived at 09:47:21.284 UTC (about 71 seconds); no retry was needed in this final run. The returned response is held in ignored tmp/diagnostic-briefing.txt, not claimed as independently fact-checked. The existing localhost service was not restarted; backend changes require a restart.
- The overlapping earlier diagnostic run, started before the final three-search/one-extraction budget was added, exhausted its timeout retries and ended with APITimeoutError. All diagnostic processes have exited; success is specific to the final bounded-research run, not every attempted call.


## 2026-10-13 - Frontend layout and report formatting refinement

- Replaced the large promotional hero and rounded cream/teal cards with a compact briefing desk: neutral gray/white surfaces, restrained blue accents, smaller controls, flat connection indicators, and tighter spacing. Kept responsive layouts, visible keyboard focus, reduced-motion support, and all existing chat/export/session behavior. Replaced promotional copy with direct instructions.
- Extended safe DOM-based Markdown rendering with italic/strikethrough emphasis, fenced code rendered as plain text, horizontal rules, wrapped paragraph joining, heading-based section containers, and quieter As of/source styling. Preserved HTTP/HTTPS-only links and fixed lost punctuation after bare URLs. Added column scopes to table headers.
- Weather briefing request instructions now ask for Conditions, Rain & wind, Travel notes, and Sources. Recognized weather headings receive monochrome decorative icons and a subtle section border. Weather metric tables display only actual model/tool-supplied content; no metrics are calculated or fabricated by the UI. The prompt instructs the model not to invent missing values or historical weather observations. Model compliance was not live-tested in this milestone. Research budgets and backend code remain unchanged.
- Verification: Node frontend checks passed, including weather section/icon counts, sources/date styling, italic/strikethrough text, literal script text in fenced code, paragraph joining, existing safe links/stream handling, prompt budgets, session behavior, and export actions. In-process GET / returned HTTP 200 and served the refined page. No live API calls were made. Browser inventory showed no enabled browser surface, so layout/native browser visual QA was not performed.


## 2026-10-14 - Multi-stage Docker packaging

- Added separate Node dependency, Python dependency, and runtime stages. npm ci uses the existing lockfile; pip installs unchanged pinned requirements and passes pip check. The final image contains the Node binary, installed dependencies, app modules, MCP manifest, frontend, and sample notes only. UID/GID 10001 runs the service; app code is not writable by that user, while /app/data is writable. The exec-form CMD runs Python as PID 1 and preserves existing PORT handling.
- Added an allowlist .dockerignore to keep credentials, local dependencies, tests/docs, and generated briefings out of the build context. No actual keys were used, printed, or copied. Updated README build/run/test instructions and the prompt log. Consulted official Docker multi-stage/build-context documentation; no tutorial application code was copied.
- Docker CLI initially had no running daemon. Started Docker Desktop with approved execution, then built assignment-1:local for linux/amd64 successfully on the ARM64 Mac. Image ID and size are recorded in docs/verification/docker-checks.md.
- Temporary container with a placeholder model key and PORT=9090 started successfully, served GET / with HTTP 200, and reported connected filesystem/Tavily/Open-Meteo MCP servers with 13/2/2 exposed tools. Verified UID 10001, read-only app code, writable data with a write/read/delete probe, and absence of excluded files. No external inference request was sent.
- Initial container test run failed three fault tests due to a hard-coded project .venv interpreter path. Fixed only the test fixture to use sys.executable. Rerun: all 23 Python tests passed in 24.766 seconds; Node frontend checks passed inside the image. Test sources were mounted read-only and are not baked into the production image.
- Stopped and automatically removed the temporary HTTP verification container; the image remains available locally. Local container verification is complete; Cloud Run deployment and deployed live behavior checks remain.
- Rechecked the three fault tests on the host using .venv/bin/python after the interpreter-path fix: all three passed in 2.300 seconds.


## 2026-10-14 - Cloud Run deployment preparation

- User selected project jd-assignment1-599 after configuring a different Google account. Verified the selected project is ACTIVE and billing enabled. Explicit project/account arguments scope every cloud operation. No existing project resources were deleted or altered.
- Added scripts/prepare_cloud_run.py and documented deployment settings. The script checks project/billing, enables Cloud Run/Artifact Registry/Secret Manager/IAM APIs, prepares a regional Docker repository and dedicated runtime account, uploads .env keys through subprocess stdin to Secret Manager, and binds Secret Accessor only on individual secrets. Model keys are never placed in Docker, shell arguments, or documentation. Runtime environment JSON contains only endpoint/model; the planned deployment pins numeric secret versions and an immutable image digest.
- Preparation targets us-west1 and the briefly service, one CPU/512 MiB, zero minimum/one maximum revision instance, concurrency eight, 600-second timeout, request-based CPU allocation, session affinity, and public assignment access. Instance-local memory and files remain ephemeral. No persistent-memory guarantees are inferred from affinity or instance limits.
- The previously built local image was absent from the current Docker daemon, so preparation rebuilds from the verified Dockerfile. At this point the required APIs, registry, runtime account, and NIM secret have been created; build/push are in progress. Tavily is keyless because its key is not set. No successful deployment or live cloud checks are claimed yet.
- Preparation CLI help and Python compilation passed. Consulted official Google Cloud secret configuration, IAM/public access, registry authentication, maximum-instance, and pricing documentation.

- Preparation completed successfully: enabled APIs, created registry/runtime identity, uploaded NIM key version 1 via stdin, granted per-secret access, built/pushed the AMD64 image, and resolved its immutable digest. Saved only non-secret environment settings and the concrete deployment command in docs/deployment. Preserved the user's current .env model nvidia/nemotron-3-ultra-550b-a55b.
- Deployed public service briefly in jd-assignment1-599/us-west1. Ready revision briefly-00001-trc serves 100% of traffic. Live URL: https://briefly-2ez6etscva-uw.a.run.app. Readiness conditions and image are recorded in docs/deployment/result.json. Actual selected runtime settings and public invoker IAM binding are separately recorded. No application backend changes were made.
- Live public HTTP verification passed: frontend HTTP 200, all three MCP connections healthy (13/2/2 exposed tools), invalid /chat HTTP 422, real NVIDIA arithmetic /chat HTTP 200 with exact {"response":"96"} shape, and real streamed filesystem read_text_file start/end plus a final response. Model calls were not mocked; no identity token was sent to the public endpoint. Evidence is docs/verification/cloud-smoke-checks.json and .md. No browser visual test, cloud search/weather invocation, memory/isolation, multi-step, or fault-injection cloud verification is claimed.
- Updated README live URL, runtime settings, repeatable prepare/deploy instructions, secret handling, cost references, and remaining milestones. Scale-to-zero is enabled; no actual billing total was measured, and no persistence across container recycling is promised.


## 2026-10-14 - Final verification and submission preparation

- Re-read all twelve assignment PDF pages with temporary pypdf 6.20.1 installed only under ignored tmp/pdf-tools. Project requirements remain unchanged. Confirmed exact diagram, process-log, source ZIP, and live-URL deliverables. Added canonical deploy.sh and enabled the listed Cloud Build API; no Cloud Build job was launched.
- All nine final public cloud checks passed with real NVIDIA/MCP calls: memory store/recall/isolation, no-tool arithmetic, weather geocoding/forecast, search/extraction/save/read-back, missing-file error and same-session recovery. Source review opened both official saved URLs successfully. Captured exact events/responses and assessment limits in cloud-final-checks.json/.md.
- The isolated live local invalid-JSON fault emitted tool_error, returned a safe HTTP 200 explanation, and recovered with a successful notes.txt read in the same session. Original inconclusive records are preserved. Fault probes were not exposed publicly.
- Final local regression passed: 23 Python tests in 18.103 seconds; all Node frontend checks; pip check. Temporary PDF and diagram tools are outside application dependency manifests. Added three implementation-specific README diagrams and cost disclosure with sourced rates, a labeled estimate, and no invented billing total. No production backend change or redeployment was needed.
- Prepared a concise process-log draft using factual history; personal learning reflection remains for the student. The student's own reflection and review are required before describing the written submission as final.

- Final documentation verification: all three README Mermaid diagrams parsed successfully with temporary Mermaid/jsdom tooling, and all relative Markdown links in README/process log/docs resolved. Temporary parsing tools were not added to package manifests. Added a credential-scanning allowlist ZIP builder and canonical deploy.sh wrapper. The current source package is a review package until the student's personal reflection and narrative review are complete. No Brightspace upload has been performed.


# Final reviews and deployment revisions


## 2026-10-14 — README submission review

Reworked README as an application/operations reference. Removed assignment/rubric comparisons, developmental commentary, personal reminders, and student-facing documentation notes; condensed duplicated interface and deployment descriptions. Retained setup/run/deploy instructions, API contracts, MCP attribution/rationale, costs, runtime limits, verification evidence, and all three diagrams. Local documentation links resolve and code fences are balanced. No application code, runtime settings, or cloud resources changed.


## 2026-10-14 — Diagram preview compatibility

Validated the three Mermaid diagrams by rendering them through Mermaid CLI with local headless Chrome. Embedded PNG versions in README so standard Markdown previews do not require Mermaid support; retained SVG exports and editable .mmd sources. Changed system/deployment layout to top-to-bottom and placed Google Cloud resources outside the local-development boundary in the deployment diagram. Inspected all three generated PNGs. Updated the source archive allowlist to include PNG diagrams. Rendering tools were installed only under ignored tmp/; app dependencies and runtime code were unchanged. The viewer itself was not identified, so lack of Mermaid support is a compatibility explanation rather than a verified viewer-specific diagnosis.


## 2026-10-14 — Portfolio frontend redesign

- Rebuilt the frontend around a forest-green research workspace with an explanatory value proposition, capability summary, a consistent setup panel, paper-like report canvas, and a project overview describing FastAPI/SDK memory, the three MCP integrations, NVIDIA NIM synthesis, and Cloud Run. All copy describes actual behavior; the initial example is explicitly marked an illustrative format preview rather than live research. No frontend runtime dependencies or backend API changes were added.
- Improved report hierarchy: descriptive title/summary guidance, an At a glance panel, numbered development styling, implications/watchpoint/source sections, weather tables, As of styling, reference-link resolution, reading-time metadata, and source navigation. Source targets remain restricted to HTTP/HTTPS; HTML remains text. Prompt research budgets and model settings were preserved.
- Moved research activity under the composer and added request-scoped green running/completed tool tags, visible failed/retry states, timestamps and counts. Failure tags remain visible even when the model returns a response. Pending feedback, reset, source navigation, export, and follow-up session behavior were checked.
- All 23 backend tests passed in 17.937 seconds; expanded Node frontend tests passed. Headless Chrome browser checks passed at 1440px desktop and 390/768px mobile with no horizontal overflow or script errors, using explicitly intercepted UI fixtures. Checks exercised guided submission, report/source styling, source jump, running/failure/completion tags, weather formatting, and reset. Inspected desktop, report, and mobile screenshots; the fixture checks are not live inference evidence. Temporary Puppeteer/formatter tools remain under ignored tmp/.
- Built and pushed the updated Linux AMD64 image, preserving existing deployed model, pinned secret versions, and resource settings. Deployment and a separate real model/UI check are in progress; no live-success claim is made at this point.

- Published revision briefly-00002-ds6 and confirmed it serves all traffic. Only the image reference changed; the existing model, pinned secret version, runtime identity, and resource settings were retained. Saved the previous deployment result as revision history.
- Actual Chrome browser check on the deployed page passed: guided Los Angeles weather request used real geocoding and weather_forecast, returned a structured report, and showed completed Location resolved / Forecast retrieved / Response ready tags without a remaining spinner. No browser script errors occurred. The page reported 35 seconds and 178 words. Captured exact events/output and screenshots in docs/verification/frontend-portfolio-live.json and frontend-portfolio.md. This UI/tool check is not independent fact-checking of every generated weather claim.


## 2026-10-14 — Single-chat workspace refinement

Removed the left briefing form, its event handlers/prompt builder, and obsolete form styling. The compact chat now opens with “Ask a question. Or ask for a brief.”, one short explanation, and three example buttons that prefill editable text without submitting. Removed the fixed message-pane height and its large empty preview; report content uses the available width. Project details are collapsed, tool connectivity is a compact row, and green activity remains directly under the composer. Freeform request guidance preserves date context, bounded research, safe source formatting, and weather instructions without routing requests by keywords.

Updated Node tests passed for example prefill/edit/send, no auto-submission, empty input, prompt guidance, formatting, sessions, exports, and live activity. Real Chrome desktop/mobile checks passed with intercepted fixtures at 1440/390/768px: compact initial message area, no left form, no horizontal overflow or script errors, editable examples, source navigation, report rendering, and reset. Browser testing caught a missing project-link ID; it was corrected before the passing run. No backend or model/secret/resource settings changed. Deployment and a separate live flow check follow.

Published revision briefly-00003-2xl and refreshed runtime metadata. A real Chrome run on the public page verified the weather example prefills without an automatic request, accepts an edit, and sends only after explicit submission. Real geocoding/forecast calls returned a structured weather briefing; tags completed and no browser script errors occurred. Preserved exact events/output and separate fixture/live screenshots in docs/verification/frontend-single-chat-live.json and frontend-single-chat.md. The backend API and deployment settings were unchanged.


## 2026-10-14 — Switch deployed model to Lightning

Changed local .env, .env.example, README, and Cloud Run environment to nvidia/nemotron-3.5-lightning-30b-a3b. The client fallback already uses this model. Redeployed the same image as revision briefly-00004-4z5, serving 100% of traffic; verified the deployed model setting and all three MCP connections. Preserved the preceding deployment result.

Live direct arithmetic passed. The first filesystem check failed: Lightning answered with invented file contents without emitting a tool call. A fresh-session follow-up explicitly requiring read_file succeeded, with actual tool completion and the expected file contents. Both outcomes are retained in docs/verification/lightning-switch.json and lightning-switch-recheck.json. This small smoke check is not a comparative speed benchmark or comprehensive tool-reliability evaluation.


## 2026-10-14 — Tool reliability comparison and return to Ultra

Compared Lightning and Ultra through the actual AgentClient with unchanged instructions and real MCPs. Fresh sessions and random file names/contents prevented file evidence from being guessed from the prompt. Lightning skipped all five tool-dependent checks, inventing file contents/errors and a max-turn error with no corresponding tool execution; arithmetic passed. Ultra passed three exact random file reads, geocoding/forecast, search, and no-tool arithmetic (6/6). Exact outcomes are in docs/verification/model-tool-comparison.json; scripts/verify_model_tools.py preserves the procedure. This is workload evidence, not a guarantee of universal reliability.

Restored Ultra in local .env, setup example, client fallback, deployment preparation fallback, README, and deployment environment. Historical verification records retain the model actually tested. No keyword router, forced tool call, or hidden retry of fabricated answers was added. Deployment and regression verification follow.

All 23 backend tests passed in 17.824 seconds. Published revision briefly-00005-b42 serving 100% of traffic. A public-endpoint check confirmed the deployed Ultra model, all three MCP connections, correct direct arithmetic, and an actual file read with the expected first line. Evidence: docs/verification/ultra-restored-live.json. Refreshed deployment metadata and rebuilt the submission archive after recording these outcomes.


## 2026-10-14 — Assignment-prefixed Cloud Run URL

Read the PDF deployment/submission sections: csci599-a1 is the sample service name and the URL is labeled an example. Verified official Google Cloud documentation: the hash portion of run.app URLs is assigned, not user-selected. Deployed the existing immutable image as csci599-a1-briefly, preserving Ultra, secrets, identity, and resource settings. New URL: https://csci599-a1-briefly-2ez6etscva-uw.a.run.app; ready revision csci599-a1-briefly-00001-clb, serving all new-service traffic. Original briefly service was retained for existing links.

Public frontend HTTP 200, all three MCP connections, direct arithmetic, and real filesystem read passed. Deployed model and public invoker policy verified. Evidence: docs/verification/assignment-url-live.json. Updated the preparation script default, current deployment records, README, checklist, and submission archive. Historical test outputs retain their original endpoints. No application logic changed.


## 2026-10-14 — Exact assignment service name

Changed the deployment service to csci599-a1 to follow the PDF example exactly. Deployed the existing image with unchanged Ultra model, secrets, identity, and resource settings. New submission URL: https://csci599-a1-2ez6etscva-uw.a.run.app. Ready revision csci599-a1-00001-p9d serves 100% of service traffic. Verified public frontend HTTP 200, all three connected MCPs, correct arithmetic, and real filesystem read. Confirmed the deployed Ultra setting and public invoker policy. Evidence: docs/verification/assignment-exact-url-live.json. Updated current setup/deployment/submission references and rebuilt the archive. Earlier services were not deleted; historical evidence retains its original endpoints.


## 2026-10-14 — Repository and final submission preparation

Excluded both local assignment handout PDFs and generated data files from Git while retaining them locally. Dependencies, .env, caches, temporary tools, and build/submission outputs remain ignored. Consolidated PROCESS_LOG.md to the required sections, retaining the 258-word development narrative and existing personal reflection verbatim; moved detailed dated entries here. Removed stale missing-reflection claims while asking the student to confirm the required §6.1 focus.

Cleaned the model comparison script, added a main guard and default temporary evidence output, and changed cloud verification to preserve historical evidence by default. The archive builder now checks narrative length, requires an existing reflection, and exports standalone README.md alongside the other deliverables. No application runtime code or dependencies changed.

Final local verification: all 23 Python tests passed in 17.787 seconds; all 10 Node frontend checks passed; pip check and installed dependency-pin checks passed. The final live run on csci599-a1 passed all nine behavioral checks (docs/verification/submission-live-checks.json); two provider errors recovered through the existing bounded retry policy. These tests do not independently establish every generated fact or source statement. Candidate Git files and archive contents were scanned for actual local credentials and common key patterns; no matches. Local Markdown links and archive integrity checked. No commit, push, or Brightspace upload performed. No Git remote is configured. Assignment source-sharing restriction means the GitHub repository should be private.
