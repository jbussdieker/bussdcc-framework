from typing import Optional
from dataclasses import dataclass

from bussdcc.events import EventSchema


@dataclass(slots=True)
class SystemIdentityEvent(EventSchema):
    name = "system.identity"

    hostname: str
    model: Optional[str]
    serial: Optional[str]
