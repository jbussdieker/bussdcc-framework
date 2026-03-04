from dataclasses import dataclass

from bussdcc.message import Message


@dataclass(slots=True, frozen=True)
class WebInterfaceStarted(Message):
    host: str
    port: int
