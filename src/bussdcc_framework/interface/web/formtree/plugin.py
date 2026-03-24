from flask import Blueprint

from bussdcc import ContextProtocol

from ..base import FlaskApp
from ..protocol import WebPlugin
from .types import (
    FieldOption,
    TreeNode,
    TreeField,
    TreeList,
    TreeListEntry,
    TreeMapping,
    TreeMappingEntry,
)


class FormtreePlugin:
    name = "formtree"

    def init_app(self, app: FlaskApp, ctx: ContextProtocol) -> None:
        app.jinja_env.tests["tree_node"] = lambda x: isinstance(x, TreeNode)
        app.jinja_env.tests["tree_field"] = lambda x: isinstance(x, TreeField)
        app.jinja_env.tests["tree_list"] = lambda x: isinstance(x, TreeList)
        app.jinja_env.tests["tree_list_entry"] = lambda x: isinstance(x, TreeListEntry)
        app.jinja_env.tests["tree_mapping"] = lambda x: isinstance(x, TreeMapping)
        app.jinja_env.tests["tree_mapping_entry"] = lambda x: isinstance(
            x, TreeMappingEntry
        )
        app.jinja_env.tests["field_option"] = lambda x: isinstance(x, FieldOption)

        bp = Blueprint(
            "bussdcc_framework_formtree",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/_framework/formtree/static",
        )
        app.register_blueprint(bp)


plugin: WebPlugin = FormtreePlugin()
