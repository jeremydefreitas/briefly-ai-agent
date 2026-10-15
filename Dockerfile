# Install each dependency set separately; only runtime artifacts reach the final image.
FROM node:22-bookworm-slim AS node-deps
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund

FROM python:3.13-slim-bookworm AS python-deps
WORKDIR /build
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --no-cache-dir -r requirements.txt \
    && /opt/venv/bin/python -m pip check

FROM python:3.13-slim-bookworm AS runtime
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
    PORT=8080
WORKDIR /app
COPY --from=python-deps /opt/venv /opt/venv
COPY --from=node-deps /usr/local/bin/node /usr/local/bin/node
COPY --from=node-deps /build/node_modules ./node_modules
COPY main.py agent_client.py mcp_client.py activity.py mcp_servers.json ./
COPY static/ ./static/
COPY data/notes.txt ./data/notes.txt
RUN groupadd --gid 10001 agent \
    && useradd --uid 10001 --gid agent --no-create-home --shell /usr/sbin/nologin agent \
    && chown -R agent:agent /app/data
USER 10001:10001
EXPOSE 8080
CMD ["python", "main.py"]
