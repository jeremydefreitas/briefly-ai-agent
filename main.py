"""HTTP entry point for the assignment agent."""

import asyncio
import json
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Annotated

import uvicorn
from agents import AgentsException
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from mcp import MCPError
from openai import APIConnectionError, APITimeoutError, InternalServerError, OpenAIError, RateLimitError
from pydantic import BaseModel, StringConstraints, ValidationError

from agent_client import AgentClient
from activity import EventSink
from mcp_client import connect_mcp_servers

load_dotenv(Path(__file__).with_name(".env"))


class ChatRequest(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    session_id: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)
    ]


class ChatResponse(BaseModel):
    response: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with connect_mcp_servers() as servers:
        client = AgentClient(mcp_servers=servers)
        app.state.agent_client = client
        try:
            yield
        finally:
            await client.close()


app = FastAPI(title="Assignment 1 Agent", lifespan=lifespan)


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(Path(__file__).with_name("static") / "index.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    client: AgentClient = request.app.state.agent_client
    return ChatResponse(response=await run_chat(client, body))


async def run_chat(client: AgentClient, body: ChatRequest, on_event: EventSink | None = None) -> str:
    try:
        return await client.chat(body.query, body.session_id, on_event=on_event)
    except APITimeoutError:
        raise HTTPException(504, "The model service timed out. Please retry.") from None
    except RateLimitError:
        raise HTTPException(503, "The model service is rate limited. Please retry later.") from None
    except APIConnectionError:
        raise HTTPException(503, "The model service is unavailable. Please retry.") from None
    except InternalServerError:
        raise HTTPException(502, "The model service failed after retries. Please try again shortly.") from None
    except (OpenAIError, AgentsException, MCPError, ValidationError):
        raise HTTPException(502, "The agent could not complete the request.") from None


@app.get("/mcp/status")
async def mcp_status(request: Request) -> dict:
    return {"servers": await request.app.state.agent_client.mcp_status()}


@app.post("/chat/stream")
async def chat_stream(body: ChatRequest, request: Request) -> StreamingResponse:
    client: AgentClient = request.app.state.agent_client

    async def events():
        queue: asyncio.Queue = asyncio.Queue()

        async def run():
            try:
                response = await run_chat(client, body, on_event=queue.put_nowait)
                queue.put_nowait({"type": "response", "response": response, "message": "Response ready."})
            except HTTPException as error:
                queue.put_nowait({"type": "error", "message": error.detail, "status_code": error.status_code})
            except Exception:
                queue.put_nowait({"type": "error", "message": "The agent could not complete the request."})
            finally:
                queue.put_nowait(None)

        task = asyncio.create_task(run())
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=10)
                except TimeoutError:
                    event = {"type": "heartbeat"}
                if event is None:
                    break
                yield json.dumps(event) + "\n"
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    return StreamingResponse(events(), media_type="application/x-ndjson", headers={
        "Cache-Control": "no-cache", "X-Accel-Buffering": "no",
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
