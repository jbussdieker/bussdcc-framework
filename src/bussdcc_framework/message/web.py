from dataclasses import dataclass

from bussdcc.message import Message


@dataclass(slots=True)
class WebInterfaceStarted(Message):
    name = "interface.web.started"

    host: str
    port: int
