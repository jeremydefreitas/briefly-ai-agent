"""Compare live tool selection with real MCPs and unpredictable file evidence.

This opt-in check uses NVIDIA and external research services. Results go to tmp/
by default so historical verification evidence is not overwritten.
"""

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_client import AgentClient
from mcp_client import FILES_ROOT, connect_mcp_servers

MODELS = (
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "nvidia/nemotron-3-ultra-550b-a55b",
)


async def check_query(client, index):
    marker = uuid.uuid4().hex
    path = FILES_ROOT / f"reliability-{marker}.txt"
    expected = "Verification marker " + uuid.uuid4().hex
    if index < 3:
        path.write_text(expected + "\n")
        query = (
            f"Read {path.name} using the filesystem tool and quote its first line. "
            "Do not modify files."
        )
        kind, required = "filesystem", {"read_file", "read_text_file"}
    elif index == 3:
        query = (
            "What is the weather in Los Angeles, California today? "
            "Include units and local time. Keep it under 100 words."
        )
        kind, required = "weather", {"geocoding", "weather_forecast"}
    elif index == 4:
        query = (
            "Search the web for the official Model Context Protocol documentation "
            "and give me its URL. Use at most one search."
        )
        kind, required = "search", {"tavily_search"}
    else:
        query = "What is 17 times 19? Answer with only the number. No tools needed."
        kind, required = "direct", set()

    events = []
    start = time.monotonic()
    answer, error = None, None
    try:
        answer = await client.chat(query, "comparison-" + marker, on_event=events.append)
    except Exception as exc:
        error = type(exc).__name__
    finally:
        path.unlink(missing_ok=True)

    tools = {event["tool"] for event in events if event["type"] == "tool_end"}
    if kind == "filesystem":
        passed = bool(tools & required) and expected in (answer or "")
    elif kind == "direct":
        passed = answer == "323" and not tools
    else:
        passed = required <= tools and bool(answer)
    result = {
        "kind": kind, "query": query,
        "elapsed_seconds": round(time.monotonic() - start, 2),
        "tools": sorted(tools), "passed": passed and error is None,
        "error": error, "response": answer, "events": events,
    }
    if kind == "filesystem":
        result["expected_first_line"] = expected
    return result


async def compare(models, output):
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": (
            "Actual AgentClient and installed MCPs with unchanged instructions; "
            "fresh session per query; random file content not disclosed to model."
        ),
        "checks": [],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    original_model = os.environ.get("OPENAI_MODEL")
    try:
        async with connect_mcp_servers() as servers:
            if len(servers) != 3:
                raise RuntimeError("All three MCP servers must connect for this comparison.")
            for model in models:
                os.environ["OPENAI_MODEL"] = model
                client = AgentClient(servers)
                try:
                    for index in range(6):
                        result = {"model": model, **await check_query(client, index)}
                        report["checks"].append(result)
                        output.write_text(json.dumps(report, indent=2) + "\n")
                        print(model, result["kind"], result["passed"],
                              result["elapsed_seconds"], result["tools"], flush=True)
                finally:
                    await client.close()
    finally:
        if original_model is None:
            os.environ.pop("OPENAI_MODEL", None)
        else:
            os.environ["OPENAI_MODEL"] = original_model
    print("Evidence: " + str(output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=list(MODELS))
    parser.add_argument("--output", type=Path, default=ROOT / "tmp/model-tool-comparison.json")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    asyncio.run(compare(args.models, args.output))


if __name__ == "__main__":
    main()
