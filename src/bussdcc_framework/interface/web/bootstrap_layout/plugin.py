from flask import Blueprint

from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin


class BootstrapLayoutPlugin:
    name = "bootstrap-layout"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        bp = Blueprint(
            "bussdcc_framework_bootstrap_layout",
            __name__,
            template_folder="templates",
        )
        app.register_blueprint(bp)


plugin: WebPlugin = BootstrapLayoutPlugin()
