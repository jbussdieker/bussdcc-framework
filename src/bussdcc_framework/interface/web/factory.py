from typing import Any, Optional, TypedDict, Iterable

from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap5  # type: ignore[import-untyped]

from bussdcc import ContextProtocol
from bussdcc_framework import json as framework_json

from .base import FlaskApp
from .plugins import load_plugins
from .protocol import WebPlugin


class FlaskAppKwargs(TypedDict, total=False):
    template_folder: str
    static_folder: str


def create_app(
    ctx: ContextProtocol,
    import_name: str,
    template_folder: Optional[str] = None,
    static_folder: Optional[str] = None,
    plugins: Iterable[WebPlugin] | None = None,
) -> FlaskApp:
    kwargs: FlaskAppKwargs = {}

    if template_folder is not None:
        kwargs["template_folder"] = template_folder

    if static_folder is not None:
        kwargs["static_folder"] = static_folder

    app = FlaskApp(import_name, **kwargs)

    Bootstrap5(app)
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        json=framework_json,
    )

    app.ctx = ctx
    app.socketio = socketio

    @app.context_processor
    def get_context() -> dict[str, Any]:
        runtime_version = ctx.state.get("runtime.version")
        framework_version = ctx.state.get("framework.version")
        app_version = ctx.state.get("app.version")
        system_identity = ctx.state.get("system.identity")

        return dict(
            runtime_version=runtime_version,
            framework_version=framework_version,
            app_version=app_version,
            system_identity=system_identity,
        )

    load_plugins(app, ctx, explicit_plugins=plugins)

    return app
