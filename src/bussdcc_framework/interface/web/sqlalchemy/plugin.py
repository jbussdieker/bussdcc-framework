from bussdcc import ContextProtocol

from .. import BaseWebPlugin, FlaskApp, WebPlugin

from .database import db


class SqlAlchemyPlugin(BaseWebPlugin):
    name = "sqlalchemy"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        db.init_app(app)


plugin = SqlAlchemyPlugin()
