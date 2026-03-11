from typing import Optional
from abc import abstractmethod
import threading

from werkzeug.serving import make_server
from flask_socketio import SocketIO

from bussdcc import Process, ContextProtocol, Event
from bussdcc_framework import message

from .base import FlaskApp
from .factory import create_app


class WebInterface(Process):
    name = "web"

    def __init__(
        self,
        import_name: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
        template_folder: Optional[str] = None,
        static_folder: Optional[str] = None,
    ) -> None:
        self.import_name = import_name or __name__
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.host = host
        self.port = port
        self._thread: threading.Thread | None = None

    def register_routes(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        pass

    def register_socketio(self, socketio: SocketIO, ctx: ContextProtocol) -> None:
        pass

    def start(self, ctx: ContextProtocol) -> None:
        self.app = create_app(
            ctx, self.import_name, self.template_folder, self.static_folder
        )
        self.socketio = self.app.socketio

        self.register_routes(self.app, ctx)
        self.register_socketio(self.socketio, ctx)

        self._thread = threading.Thread(
            target=self._run,
            name=self.name,
            daemon=True,
        )
        self._thread.start()
        ctx.emit(message.WebInterfaceStarted(host=self.host, port=self.port))

    def _run(self) -> None:
        self._server = make_server(
            host=self.host,
            port=self.port,
            app=self.app,
            threaded=True,
        )

        self._server.serve_forever()

    def stop(self, ctx: ContextProtocol) -> None:
        server = getattr(self, "_server", None)
        if server:
            server.shutdown()

        if self._thread:
            self._thread.join(timeout=5)
