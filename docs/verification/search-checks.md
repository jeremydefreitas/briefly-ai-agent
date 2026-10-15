# Live verification: Tavily selection and multi-step tool use

Run on 2026-10-12 (America/Los_Angeles); JSON timestamps use UTC.

Both checks used live NVIDIA inference and real MCP subprocesses through the
actual FastAPI POST /chat route with an in-process HTTP transport. Activity was
recorded without replacing model or tool results. Tavily used keyless mode.

| Check | HTTP | Actual completed tools | Outcome |
| --- | --- | --- | --- |
| Search for official MCP documentation and cite sources | 200 | tavily_search | Passed for tool selection and relevant official links |
| Search for official MCP documentation and save a summary with URLs | 200 | tavily_search, then write_file | Passed for the multi-step tool workflow and file creation |

## Evidence reviewed

- The first response cited relevant official documentation and repository URLs.
  The official versioned specification and getting-started links opened successfully.
- The second run performed two sequential tool calls across the two MCP servers,
  with model steps between them and successful completion events for both.
- Independently inspected `data/verification-summary.txt`: it exists, contains a
  substantive MCP summary and source URLs, and matches the JSON evidence snapshot.
- No tool errors occurred in either run. The test did not substitute hard-coded
  tool responses or force tools through application keyword routing.

## Source-quality caveat

The saved file puts an alternative documentation mirror
(`modelcontextprotocol.info`) under its Official Sources heading. That site should
be distinguished from the official project sources. The first response also
cited an SDK documentation URL that the review browser could not access; that
URL's validity is inconclusive. These checks establish real tool use and a working
search/write chain, not the correctness of every claim or URL in the answers.

Exact prompts, complete responses, timestamps, events, source checks, assessments,
and the saved-file snapshot are in [search-checks.json](search-checks.json).

Next live checks: memory recall, session isolation, and recovery after a tool error.
Source-selection instructions should also be tightened and verified.
