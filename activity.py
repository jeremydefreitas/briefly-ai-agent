"""Request-scoped operational events for the browser chat."""

from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Callable

from agents import RunHooks

EventSink = Callable[[dict], None]
activity_sink: ContextVar[EventSink | None] = ContextVar("activity_sink", default=None)


def emit_activity(event_type: str, message: str, **details) -> None:
    sink = activity_sink.get()
    if sink is not None:
        sink({
            "type": event_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **details,
        })


class ActivityHooks(RunHooks):
    async def on_llm_start(self, context, agent, system_prompt, input_items) -> None:
        emit_activity("model_start", "Agent is asking the model for the next step.")

    async def on_llm_end(self, context, agent, response) -> None:
        emit_activity("model_end", "Model response received.")
