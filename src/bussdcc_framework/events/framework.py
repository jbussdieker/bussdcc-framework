from typing import Optional
from dataclasses import dataclass

from bussdcc.events import EventSchema


@dataclass(slots=True)
class FrameworkBooted(EventSchema):
    name = "framework.booted"

    version: str


@dataclass(slots=True)
class FrameworkShuttingDown(EventSchema):
    name = "framework.shutting_down"

    version: str
    reason: Optional[str]
