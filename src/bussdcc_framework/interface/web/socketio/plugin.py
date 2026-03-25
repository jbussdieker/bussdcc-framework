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
            static_url_path="/_framework/socketio/static",
        )

        app.config.setdefault("SOCKETIO_RECONNECT", True)
        app.config.setdefault("SOCKETIO_RECONNECT_ATTEMPTS", None)
        app.config.setdefault("SOCKETIO_RECONNECT_DELAY", 1000)
        app.config.setdefault("SOCKETIO_RECONNECT_DELAY_MAX", 5000)

        @app.context_processor
        def socketio_template_context() -> dict[str, object]:
            return {
                "framework_socketio": {
                    "reconnect": app.config["SOCKETIO_RECONNECT"],
                    "reconnect_attempts": app.config["SOCKETIO_RECONNECT_ATTEMPTS"],
                    "reconnect_delay": app.config["SOCKETIO_RECONNECT_DELAY"],
                    "reconnect_delay_max": app.config["SOCKETIO_RECONNECT_DELAY_MAX"],
                }
            }

        app.register_blueprint(bp)


plugin: WebPlugin = SocketIOPlugin()
