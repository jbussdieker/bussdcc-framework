from typing import Any

from flask import render_template
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap5  # type: ignore[import-untyped]

from bussdcc.context import ContextProtocol

from .base import FlaskApp


def create_app(ctx: ContextProtocol) -> FlaskApp:
    app = FlaskApp(__name__)
    Bootstrap5(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    app.ctx = ctx
    app.socketio = socketio

    @app.context_processor
    def get_context() -> dict[str, Any]:
        app_name = ctx.state.get("app.name")
        app_version = ctx.state.get("app.version")
        system_identity = ctx.state.get("system.identity")
        runtime_version = ctx.state.get("runtime.version")

        return dict(
            app_name=app_name,
            app_version=app_version,
            system_identity=system_identity,
            runtime_version=runtime_version,
        )

    @app.route("/")
    def home() -> str:
        return render_template("home.html")

    return app
