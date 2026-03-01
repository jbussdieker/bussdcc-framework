from typing import Optional
from dataclasses import dataclass

from bussdcc.events import EventSchema


@dataclass(slots=True)
class SinkHandlerError(EventSchema):
    name = "sink.handler.error"
