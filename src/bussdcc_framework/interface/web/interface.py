from typing import Optional, Iterable
import threading

from werkzeug.serving import make_server
from flask_socketio import SocketIO

from bussdcc import Process, ContextProtocol, Event, Message
from bussdcc_framework import message

from .base import FlaskApp
from .factory import create_app
from .plugins import PluginSpec, resolve_plugins
from .protocol import WebPlugin


class WebInterface(Process):
    name = "web"

    def __init__(
        self,
        import_name: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
        template_folder: Optional[str] = None,
        static_folder: Optional[str] = None,
        plugins: Iterable[PluginSpec] | None = None,
    ) -> None:
        self.import_name = import_name or __name__
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.plugins = list(plugins) if plugins is not None else []
        self.host = host
        self.port = port
        self._thread: threading.Thread | None = None
        self._plugins: list[WebPlugin] = []
        self._event_handlers: dict[type[Message], list[WebPlugin]] = {}

    def iter_plugins(self) -> Iterable[PluginSpec]:
        return []

    def register_routes(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        pass

    def register_socketio(self, socketio: SocketIO, ctx: ContextProtocol) -> None:
        pass

    def start(self, ctx: ContextProtocol) -> None:
        plugin_specs = [*self.iter_plugins(), *self.plugins]
        self._plugins = resolve_plugins(plugin_specs)
        self._event_handlers = self._build_event_handlers(self._plugins)

        self.app = create_app(
            ctx,
            self.import_name,
            self.template_folder,
            self.static_folder,
            plugins=self._plugins,
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

    def _build_event_handlers(
        self,
        plugins: Iterable[WebPlugin],
    ) -> dict[type[Message], list[WebPlugin]]:
        handlers: dict[type[Message], list[WebPlugin]] = {}

        for plugin in plugins:
            for event_type in plugin.event_types():
                handlers.setdefault(event_type, []).append(plugin)

        return handlers

    def handle_event(self, ctx: ContextProtocol, evt: Event[Message]) -> None:
        app = getattr(self, "app", None)
        socketio = getattr(self, "socketio", None)

        if app is None or socketio is None:
            return

        seen: set[str] = set()

        for cls in type(evt.payload).__mro__:
            if cls is object:
                continue

            for plugin in self._event_handlers.get(cls, ()):
                if plugin.name in seen:
                    continue

                plugin.handle_event(app, socketio, ctx, evt)
                seen.add(plugin.name)

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
