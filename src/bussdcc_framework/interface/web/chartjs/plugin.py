from flask import Blueprint

from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin


class ChartJSPlugin:
    name = "chartjs"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        bp = Blueprint(
            "bussdcc_framework_chartjs",
            __name__,
            template_folder="templates",
            static_folder="static",
        )

        app.register_blueprint(bp)


plugin: WebPlugin = ChartJSPlugin()
