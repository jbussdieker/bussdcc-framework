from typing import Iterable

from flask_socketio import SocketIO

from bussdcc import ContextProtocol, Event, Message

from .base import FlaskApp


class BaseWebPlugin:
    name = "base"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        pass

    def event_types(self) -> Iterable[type[Message]]:
        return ()

    def handle_event(
        self,
        app: FlaskApp,
        socketio: SocketIO,
        ctx: ContextProtocol,
        evt: Event[Message],
    ) -> None:
        pass
