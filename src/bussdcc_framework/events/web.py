from dataclasses import dataclass

from bussdcc.events import EventSchema


@dataclass(slots=True)
class WebInterfaceStarted(EventSchema):
    name = "interface.web.started"

    host: str
    port: int
