from typing import Protocol, runtime_checkable

from bussdcc import ContextProtocol

from .base import FlaskApp


@runtime_checkable
class WebPlugin(Protocol):
    name: str

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None: ...
