from flask import Blueprint

from bussdcc import ContextProtocol

from .. import BaseWebPlugin, FlaskApp, WebPlugin


class BootstrapPlugin(BaseWebPlugin):
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


plugin = BootstrapPlugin()
