from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin
from .database import db


class SqlAlchemyPlugin:
    name = "sqlalchemy"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        db.init_app(app)


plugin: WebPlugin = SqlAlchemyPlugin()
