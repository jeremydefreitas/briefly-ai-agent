# Final deployed verification

Run on 2026-10-14 against the public Cloud Run service. Exact prompts, session IDs,
responses, events, elapsed times, and assessments are in cloud-final-checks.json.
Requests used /chat/stream for real-time tool evidence; the separate deployment
smoke report verifies the required JSON POST /chat contract with live inference.
No model or MCP response was mocked. The verification script is
`scripts/verify_cloud_run.py`; reruns create a unique session/file suffix and
replace the latest final-check report. Earlier deployment evidence is separate.

| Check | HTTP | Time | Result | Observed behavior |
| --- | --- | --- | --- | --- |
| memory-store | 200 | 1.2s | passed | Codename acknowledged without tools. |
| memory-recall | 200 | 1.7s | passed | Same session recalled the exact unique codename. |
| memory-isolation | 200 | 2.1s | passed | New session did not inherit the codename. |
| no-tool | 200 | 12.5s | passed | Returned 323 for 17 × 19; zero tool calls. |
| weather | 200 | 18.4s | passed | Real geocoding then weather_forecast; returned Fahrenheit values and a local date/time. |
| search-and-save | 200 | 27.2s | passed | Real Tavily search/extract followed by filesystem write_file. |
| read-saved-summary | 200 | 11.3s | passed | Real read_text_file returned the saved summary and two official source URLs. |
| missing-file | 200 | 10.4s | passed | Real read_text_file error; model explained the missing file without creating it. |
| recovery | 200 | 2.4s | passed | Same session subsequently read notes.txt and quoted its actual first line. |

## Source review and limits

The read-back summary cites only the official modelcontextprotocol.io site and
its modelcontextprotocol/modelcontextprotocol GitHub repository. Both URLs were
opened independently and served the expected project documentation. The old
mirror-labeling error did not recur in this run, whose query explicitly requested
official sources and correct mirror labels. This is evidence for the inspected
response, not a guarantee that all generated citations or facts will be correct.

Weather events establish actual successful geocoding/forecast calls. The final
answer displays units and local time; public operational events omit tool
arguments/results by design, so exact weather values were not independently
matched to that request's complete API payload. The earlier local weather report
contains captured arguments and reference data.

Memory checks were consecutive within a running instance. They establish
same-session recall and different-session isolation, not durable persistence
through recycling. The saved verification file is also ephemeral and its contents
are preserved in JSON evidence. It need not survive scale-to-zero for grading.

## Failure coverage

Missing-file execution failure and same-session recovery passed on Cloud Run.
Controlled real-stdio tests cover disconnect, invalid JSON, and invalid schemas.
Live local malformed-JSON verification also now passed with the currently deployed
NVIDIA model; see fault-checks-final-live.json. This fixture was never added to the
public production service. No injected malformed-protocol Cloud Run test or
automatic MCP reconnection is claimed.
