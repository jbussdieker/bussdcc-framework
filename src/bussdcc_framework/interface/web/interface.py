import threading
from abc import abstractmethod

from bussdcc.process import Process
from bussdcc.context import ContextProtocol
from bussdcc.event import Event

from bussdcc_framework import events

from werkzeug.serving import make_server

from .factory import create_app


class WebInterface(Process):
    name = "web"

    def __init__(self, host: str, port: int) -> None:
        self._thread: threading.Thread | None = None
        self.host = host
        self.port = port

    @abstractmethod
    def register_routes(self, ctx: ContextProtocol) -> None: ...

    def start(self, ctx: ContextProtocol) -> None:
        self.app = create_app(ctx)
        self.socketio = self.app.socketio
        self.register_routes(ctx)
        self._thread = threading.Thread(
            target=self._run,
            name=self.name,
            daemon=True,
        )
        self._thread.start()
        ctx.emit(events.WebInterfaceStarted(host=self.host, port=self.port))

    def _run(self) -> None:
        self._server = make_server(
            host=self.host,
            port=self.port,
            app=self.app,
            threaded=True,
        )

        self._server.serve_forever()

    def stop(self, ctx: ContextProtocol) -> None:
        if hasattr(self, "_server"):
            self._server.shutdown()

        if self._thread:
            self._thread.join(timeout=5)
