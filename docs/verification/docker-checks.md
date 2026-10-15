# Docker verification

Verified on 2026-10-14 using Docker Desktop on an ARM64 Mac, with a Linux AMD64
image running under Docker's emulation. This is local verification, not Cloud Run.

- Build: `docker build --platform linux/amd64 -t assignment-1:local .` passed.
- Image ID: `sha256:af9ca772243cdf8ab31ec397813c369bf58a8ce9852fd60ac83fe24bfcb09f7f`.
- Docker-reported image size: 124,668,357 bytes (about 124.7 MB).
- Python pinned dependency installation and `pip check` passed during build.
- Runtime user: UID/GID `10001:10001`.

| Check | Actual result |
| --- | --- |
| Start with placeholder key and PORT=9090 | Uvicorn PID 1 listens on 0.0.0.0:9090; startup completes |
| GET / | HTTP 200; serves the Briefing desk UI |
| GET /mcp/status | All three servers connected; filesystem 13 tools, Tavily 2, Open-Meteo 2 |
| Runtime permissions | UID 10001 can write/read/delete a probe under /app/data; cannot write main.py |
| Files excluded from runtime | .env, .venv, .git, tmp, tests, docs, and generated verification-summary.txt absent |
| Python suite in container | All 23 tests passed in 24.766 seconds |
| Frontend suite in container | All Node checks passed, including streaming, formatting, weather sections, exports, and sessions |
| Shutdown | Temporary container stopped and automatically removed |

The first Python suite run passed 20 tests but failed three fault tests because
the test fixture hard-coded `/app/.venv/bin/python`. Changed the test-only fixture
to `sys.executable`, matching the interpreter used to run the suite; the complete
rerun passed. No production backend change was needed.

Test sources were bind-mounted read-only for verification and are excluded from
the production image. Python tests use mocked model HTTP and real MCP subprocesses,
including filesystem invocation and protocol fault/recovery tests. HTTP startup
used a placeholder key; no NVIDIA request was sent and no credential was loaded
into the verification container. These checks establish packaging and runtime
behavior, not live external search/weather/model availability or Cloud Run behavior.
Base image version tags can advance; the image ID above identifies the tested build.
