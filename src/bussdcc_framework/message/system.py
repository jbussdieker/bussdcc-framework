from typing import Optional
from dataclasses import dataclass

from bussdcc.message import Message


@dataclass(slots=True, frozen=True)
class SystemIdentityEvent(Message):
    hostname: str
    model: Optional[str]
    serial: Optional[str]
