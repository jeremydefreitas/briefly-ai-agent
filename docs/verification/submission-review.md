# Final repository and submission review

Review date: 2026-10-14 (America/Los_Angeles).

## Repository

- Git candidates scanned against actual local credential values and common key/private-key patterns: no matches. Final documentation links and archive integrity were also checked.
- Secrets, dependencies, caches, temporary files, generated workspace files, submission outputs, and both local handout PDFs are ignored. The original local files are retained.
- No GitHub remote or commits exist. No push was attempted. Use a private repository because the assignment prohibits sharing source.
- Consolidated PROCESS_LOG.md; moved dated working entries to development history. The development narrative is 258 words. The existing personal reflection is retained unchanged; its §6.1 focus is for the student to confirm.
- Cleaned the model comparison script and made live verification output default to ignored tmp/ so reruns preserve committed evidence.

## Verification

- All 23 Python tests passed in 17.787 seconds. These use mocked external model HTTP and real MCP protocol subprocesses.
- All 10 frontend Node checks passed, including incremental activity, safe formatting, examples, session behavior, and exports.
- pip check passed; installed Python versions match requirements.txt; the three installed Node MCP packages match their pins.
- The current public service uses Ultra and the assignment's exact service name. All nine final live checks passed on the current submission URL: memory store/recall/isolation, no-tool arithmetic, geocoding/forecast, search/save, read-back, missing-file error, and same-session recovery. 2 transient model errors recovered through bounded retries. [Exact events and responses](submission-live-checks.json). Generated summaries and weather claims were not independently fact-checked in this run; prior evidence remains available.

## Deliverables

The archive builder excludes local credentials, dependencies, caches, generated briefings, and handout PDFs. It validates archive integrity, scans credentials, enforces the development narrative length, and requires a nonempty existing reflection. It writes the source ZIP, checksum, live URL, PROCESS_LOG.md, and README.md under dist/.

README includes setup/run/deploy/costs, external-server attribution, and three rendered diagrams. Historical verification evidence is retained with actual model names and URLs.

The package is prepared for manual Brightspace submission; nothing has been uploaded. Personal reflection accuracy and the deadline remain student responsibilities.
