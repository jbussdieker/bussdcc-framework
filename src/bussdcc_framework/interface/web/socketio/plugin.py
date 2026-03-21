from flask import Blueprint

from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin


class SocketIOPlugin:
    name = "socketio"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        bp = Blueprint(
            "bussdcc_framework_socketio",
            __name__,
            template_folder="templates",
            static_folder="static",
        )

        app.config.setdefault("SOCKETIO_RECONNECT_DELAY", 1000)
        app.config.setdefault("SOCKETIO_RECONNECT_DELAY_MAX", 5000)

        app.register_blueprint(bp)


plugin: WebPlugin = SocketIOPlugin()
