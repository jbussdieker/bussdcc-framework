from typing import Optional
from dataclasses import dataclass

from bussdcc.message import Message


@dataclass(slots=True)
class FrameworkBooted(Message):
    name = "framework.booted"

    version: str


@dataclass(slots=True)
class FrameworkShuttingDown(Message):
    name = "framework.shutting_down"

    version: str
    reason: Optional[str]
