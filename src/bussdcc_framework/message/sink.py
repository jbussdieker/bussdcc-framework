from typing import Optional
from dataclasses import dataclass

from bussdcc.event import Event
from bussdcc.message import Message, EventLevel


@dataclass(slots=True)
class SinkHandlerError(Message):
    name = "sink.handler.error"
    level = EventLevel.ERROR

    error: str
    evt: Event[Message] | None = None
    traceback: str | None = None
