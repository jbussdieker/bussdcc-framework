from typing import Optional
from dataclasses import dataclass

from bussdcc import Event, Message, Severity


@dataclass(slots=True, frozen=True)
class SinkHandlerError(Message):
    severity = Severity.ERROR

    sink: str
    error: str
    evt: Event[Message] | None = None
    traceback: str | None = None
