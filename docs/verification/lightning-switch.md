# Lightning model switch (historical)

Superseded: the app returned to Ultra after [comparative tool checks](model-tool-comparison.md).

Deployed revision: `briefly-00004-4z5`. Verified model: `nvidia/nemotron-3.5-lightning-30b-a3b`. All three MCPs connected.

- Initial direct arithmetic check passed.
- Initial filesystem check failed: no tool call; invented contents.
- Fresh-session explicit read_file check passed with actual tool completion and the expected file contents.

Exact events and elapsed times: [initial check](lightning-switch.json), [recheck](lightning-switch-recheck.json). These are smoke checks, not a side-by-side speed benchmark.
