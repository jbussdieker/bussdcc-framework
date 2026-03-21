from typing import Any, Optional, TypedDict, Iterable

from flask_socketio import SocketIO

from bussdcc import ContextProtocol
from bussdcc_framework import json as framework_json

from .base import FlaskApp
from .plugins import load_plugins, PluginSpec


class FlaskAppKwargs(TypedDict, total=False):
    template_folder: str
    static_folder: str


def create_app(
    ctx: ContextProtocol,
    import_name: str,
    template_folder: Optional[str] = None,
    static_folder: Optional[str] = None,
    plugins: Iterable[PluginSpec] | None = None,
) -> FlaskApp:
    kwargs: FlaskAppKwargs = {}

    if template_folder is not None:
        kwargs["template_folder"] = template_folder

    if static_folder is not None:
        kwargs["static_folder"] = static_folder

    app = FlaskApp(import_name, **kwargs)
    app.ctx = ctx
    app.socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        json=framework_json,
    )

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

    load_plugins(app, ctx, plugins=plugins)

    return app
