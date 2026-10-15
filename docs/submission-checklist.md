# Submission checklist

Final technical review: 2026-10-14. The existing personal reflection is included
and preserved as written. Its alignment with §6.1 should be confirmed by the student.

| Requirement | Status / evidence |
| --- | --- |
| Public Cloud Run URL | https://csci599-a1-2ez6etscva-uw.a.run.app; deployed revision csci599-a1-00001-p9d |
| POST /chat query/session_id → response | Public live smoke test passed; typed request/response in main.py |
| Real MCP discovery and invocation | Filesystem, Tavily, Open-Meteo; pinned manifest and actual SDK transports |
| JSON Schema tool arguments | Discovery/schema tests; successful real tool calls; local weather reference capture |
| Appropriate model tool selection | No-tool math, real file/search/weather calls; no keyword router |
| Multi-step reasoning | Cloud search → extraction → write; weather geocode → forecast |
| Framework-native memory | SDK SQLiteSession; cloud exact recall and separate-session isolation |
| Three failure modes | Real stdio disconnect/invalid-JSON/invalid-schema tests; live fault/recovery evidence; cloud missing-file recovery |
| Non-root multi-stage Docker, PORT | Linux AMD64 build, UID 10001, custom port check, 23 container tests |
| Three required diagrams | Three rendered diagrams embedded in README, with SVG and Mermaid sources |
| Third MCP rationale/attribution | README server table explains structured weather/no new key |
| Setup/run/deploy/costs | README, deploy.sh, deployment helpers, docs/costs.md |
| Process log narrative | 258-word development narrative, verification account, and dated evidence |
| Personal learning | Existing three-sentence reflection retained; confirm §6.1 focus in your own words |
| Prompt log | prompts.md; substantive instructions, no keys |
| Source ZIP | scripts/build_submission.py produces dist/assignment-1-source.zip and scans its contents |

## Student actions before uploading

- Review the development narrative and AI-tool list in PROCESS_LOG.md; correct
  anything that does not match your own work and voice.
- Confirm the existing reflection addresses what AI could not do and what you figured out yourself (§6.1). No personal experiences have been invented.
- If you edit the documents, rebuild with `.venv/bin/python scripts/build_submission.py`; submit the live URL, ZIP, and process log
  through Brightspace. Deadline and any student-identification details are in
  Brightspace; no submission to Brightspace has been performed by the assistant.
- Keep the public service available until grades are posted. The selected project
  is billed, but USC education-credit eligibility/remaining credit was not verified.

## Documented limits

Memory/files are instance-local and may disappear after recycling. Provider
availability, future citation accuracy, and browser visual layout are not
established by deterministic tests. Fault injection remains isolated from the
public service; automatic restart of a failed MCP subprocess is not implemented.
Exact weather payloads were captured locally, not in the public activity stream.
Earlier failed/inconclusive attempts are retained alongside the final successful
runs; passing tests are not claims that every historical run succeeded.

## GitHub preparation

Use a **private** repository: the assignment prohibits sharing source code. No
remote is configured and no commit or push has been made. `.gitignore` excludes
credentials, dependencies, local handouts, generated workspace files, and build
artifacts. The submission archive is generated separately under ignored `dist/`.

[Final technical review](verification/submission-review.md) records checks and limits.
