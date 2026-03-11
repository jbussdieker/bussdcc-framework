from typing import Optional
from dataclasses import dataclass

from bussdcc import Message


@dataclass(slots=True, frozen=True)
class FrameworkBooted(Message):
    version: str


@dataclass(slots=True, frozen=True)
class FrameworkShuttingDown(Message):
    version: str
    reason: Optional[str]
