# Model tool reliability comparison

Actual AgentClient, unchanged agent instructions, installed MCP servers, and live NVIDIA NIM requests. Each query used a fresh session. Three file checks per model used newly generated filenames and random contents not supplied in the prompt; files were removed afterward.

| Check | Lightning | Ultra |
| --- | --- | --- |
| Three file reads | 0/3; no tool calls, invented contents/errors | 3/3; real reads, correct random contents |
| Weather | No tool calls; invented max-turn error | Real geocoding → weather_forecast |
| Web search | URL returned without requested search | Real tavily_search |
| Direct arithmetic | Correct, no tools | Correct, no tools |

Ultra passed all six checks; Lightning passed only arithmetic. Reverted the runtime and code/setup defaults to `nvidia/nemotron-3-ultra-550b-a55b`. Tools remain selected by the agent; no keyword router or forced tool calls were added. Model-independent arithmetic continues to work without tools.

[Exact queries, events, outputs, and timings](model-tool-comparison.json). Reproduce with `.venv/bin/python scripts/verify_model_tools.py`; this makes live API calls and writes to ignored `tmp/model-tool-comparison.json`. Use `--output PATH` to save elsewhere; existing evidence is preserved by default. The separate earlier [Lightning switch](lightning-switch.md) is retained as historical evidence, not the current model configuration.

These checks demonstrate the observed reliability improvement on this workload, not a guarantee that Ultra never hallucinates. This was not a controlled inference-speed benchmark.

At the time of verification, revision `briefly-00005-b42` served 100% of the original service traffic. The current assignment-prefixed endpoint is recorded in [URL verification](assignment-exact-url.md). Verified the deployed Ultra environment, all three MCP connections, direct arithmetic, and a real filesystem read through the public endpoint. [Live smoke-check evidence](ultra-restored-live.json).
