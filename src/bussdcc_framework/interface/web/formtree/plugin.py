from flask import Blueprint

from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin
from .types import TreeNode


class FormtreePlugin:
    name = "formtree"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        app.jinja_env.tests["tree_node"] = lambda x: isinstance(x, TreeNode)

        bp = Blueprint(
            "bussdcc_framework_formtree",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/_framework/formtree/static",
        )
        app.register_blueprint(bp)


plugin: WebPlugin = FormtreePlugin()
