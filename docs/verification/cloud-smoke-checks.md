# Cloud Run deployment checks

Verified on 2026-10-14 against the actual public service, without Google identity tokens.

- URL: https://briefly-2ez6etscva-uw.a.run.app
- Project / region: jd-assignment1-599 / us-west1
- Ready revision: briefly-00001-trc
- Image: us-west1-docker.pkg.dev/jd-assignment1-599/assignment-1/briefly@sha256:9e453dc5dc0aa1cd40279fc70abc6fc30ad45d6291d73d261fc64aa563faf216

| Check | Actual result |
| --- | --- |
| Public frontend | HTTP 200; serves the Briefing desk UI |
| MCP health | HTTP 200; filesystem/Tavily/Open-Meteo connected with 13/2/2 tools |
| Invalid /chat request | HTTP 422 for a whitespace-only query |
| Live /chat and NVIDIA | HTTP 200, exact response object, answer 96 to 12 times 8 |
| Live filesystem via /chat/stream | HTTP 200; actual read_text_file start/end events and final nonempty response |

The model backend uses the current .env-selected NVIDIA model,
`nvidia/nemotron-3-ultra-550b-a55b`, preserved during deployment. Only its key
was uploaded as secret data; documentation contains secret references, not keys.
Tavily is keyless. These were real model/transport/tool calls, not mocked responses.
No files were written by the live agent check.

Actual response objects and activity events are recorded in cloud-smoke-checks.json.
Deployment readiness, pinned image/secret references, settings, and public IAM
policy are recorded under docs/deployment. Revision settings confirm concurrency
8, a 600-second timeout, maximum one instance, gen2, CPU throttling, session
affinity, and the dedicated runtime identity. IAM grants allUsers the invoker role.

This is a deployment smoke check. It does not establish all news/source accuracy,
cloud weather/search invocation, multi-step workflows, memory isolation, malformed
MCP recovery, browser visual layout, or durable storage. Those remain separate
verification tasks. Session memory and workspace files are ephemeral.
