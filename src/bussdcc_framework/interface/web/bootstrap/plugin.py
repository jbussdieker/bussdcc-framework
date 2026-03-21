from flask_bootstrap import Bootstrap5  # type: ignore[import-untyped]

from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin


class BootstrapPlugin:
    name = "bootstrap"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        Bootstrap5(app)


plugin: WebPlugin = BootstrapPlugin()
