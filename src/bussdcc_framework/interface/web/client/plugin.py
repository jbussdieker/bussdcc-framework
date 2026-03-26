from flask import Blueprint

from bussdcc import ContextProtocol

from .. import BaseWebPlugin, FlaskApp, WebPlugin


class ClientPlugin(BaseWebPlugin):
    name = "client"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        bp = Blueprint(
            "bussdcc_framework_client",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/_framework/client/static",
        )
        app.register_blueprint(bp)


plugin: WebPlugin = ClientPlugin()
