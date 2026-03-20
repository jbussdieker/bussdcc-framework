from typing import Any

from .types import TreeNode, TreeField
from .form import coerce_form_value, unwrap_optional


def _child_prefix(prefix: str, child_name: str | None) -> str:
    if not child_name:
        raise RuntimeError("Collection child must have a name")
    return f"{prefix}.{child_name}" if prefix else child_name


def _collect_row_ids(flat: dict[str, Any], prefix: str) -> list[str]:
    row_ids: list[str] = []
    seen: set[str] = set()
    needle = prefix + "."

    for key in flat.keys():
        if not key.startswith(needle):
            continue

        rest = key[len(needle) :]
        if "." not in rest:
            continue

        row_id = rest.split(".", 1)[0]
        if row_id not in seen:
            seen.add(row_id)
            row_ids.append(row_id)

    return row_ids


def _is_bool_type(tp: object) -> bool:
    return unwrap_optional(tp) is bool


def unflatten(tree: TreeNode, flat: dict[str, Any]) -> dict[str, Any]:
    def build(node: TreeNode, prefix: str = "") -> dict[str, Any]:
        result: dict[str, Any] = {}

        node_prefix = prefix
        if node.name:
            node_prefix = f"{prefix}.{node.name}" if prefix else node.name

        for field in node.fields:
            key = f"{node_prefix}.{field.name}" if node_prefix else field.name

            if _is_bool_type(field.type):
                value = flat.get(key)
            else:
                value = flat.get(key, field.value)

            result[field.name] = coerce_form_value(field.type, value)

        for child in node.children:
            if not child.name:
                raise RuntimeError("Nested child must have a name")
            result[child.name] = build(child, node_prefix)

        for tree_list in node.lists:
            prefix_for_list = _child_prefix(node_prefix, tree_list.name)
            row_ids = _collect_row_ids(flat, prefix_for_list)

            items: list[Any] = []
            for row_id in row_ids:
                row_prefix = f"{prefix_for_list}.{row_id}"

                if isinstance(tree_list.item_schema, TreeField):
                    value_key = f"{row_prefix}.value"
                    if _is_bool_type(tree_list.item_schema.type):
                        raw_value = flat.get(value_key)
                    else:
                        raw_value = flat.get(value_key, tree_list.item_schema.value)

                    items.append(
                        coerce_form_value(tree_list.item_schema.type, raw_value)
                    )
                elif isinstance(tree_list.item_schema, TreeNode):
                    items.append(build(tree_list.item_schema, row_prefix))
                else:
                    raise RuntimeError("List missing item schema")

            result[tree_list.name] = items

        for mapping in node.mappings:
            prefix_for_mapping = _child_prefix(node_prefix, mapping.name)
            row_ids = _collect_row_ids(flat, prefix_for_mapping)

            dict_items: dict[str, Any] = {}
            for row_id in row_ids:
                row_prefix = f"{prefix_for_mapping}.{row_id}"

                raw_dict_key = flat.get(f"{row_prefix}.key")
                if not isinstance(raw_dict_key, str) or raw_dict_key == "":
                    continue

                dict_key = raw_dict_key

                if isinstance(mapping.value_schema, TreeField):
                    value_key = f"{row_prefix}.value"
                    if _is_bool_type(mapping.value_schema.type):
                        raw_value = flat.get(value_key)
                    else:
                        raw_value = flat.get(value_key, mapping.value_schema.value)

                    dict_items[dict_key] = coerce_form_value(
                        mapping.value_schema.type,
                        raw_value,
                    )
                elif isinstance(mapping.value_schema, TreeNode):
                    dict_items[dict_key] = build(mapping.value_schema, row_prefix)
                else:
                    raise RuntimeError("Mapping missing value schema")

            result[mapping.name] = dict_items

        return result

    return build(tree)
