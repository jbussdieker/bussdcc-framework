from flask import Blueprint
from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin


class BootstrapPlugin:
    name = "bootstrap"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        bp = Blueprint(
            "bussdcc_framework_bootstrap",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/_framework/bootstrap/static",
        )
        app.register_blueprint(bp)


plugin: WebPlugin = BootstrapPlugin()
