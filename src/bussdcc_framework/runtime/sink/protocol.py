from typing import Protocol

from bussdcc.context.protocol import ContextProtocol
from bussdcc.event import Event


class EventSinkProtocol(Protocol):
    def start(self, ctx: ContextProtocol) -> None: ...
    def stop(self) -> None: ...
    def handle(self, evt: Event[object]) -> None: ...
