from flask import Blueprint

from bussdcc import ContextProtocol

from .. import BaseWebPlugin, FlaskApp, WebPlugin


class ChartJSPlugin(BaseWebPlugin):
    name = "chartjs"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        bp = Blueprint(
            "bussdcc_framework_chartjs",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/_framework/chartjs/static",
        )
        app.register_blueprint(bp)


plugin = ChartJSPlugin()
