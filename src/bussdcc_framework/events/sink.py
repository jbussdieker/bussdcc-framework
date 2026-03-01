from typing import Optional
from dataclasses import dataclass

from bussdcc.event import Event
from bussdcc.events import EventSchema, EventLevel


@dataclass(slots=True)
class SinkHandlerError(EventSchema):
    name = "sink.handler.error"
    level = EventLevel.ERROR

    error: str
    evt: Event[EventSchema] | None = None
    traceback: str | None = None
