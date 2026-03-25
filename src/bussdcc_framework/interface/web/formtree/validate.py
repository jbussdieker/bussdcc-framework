from dataclasses import replace
from typing import Any

from bussdcc_framework.codec import UNHANDLED, load_atomic

from .form import coerce_form_value, unwrap_optional
from .types import (
    TreeField,
    TreeList,
    TreeListEntry,
    TreeMapping,
    TreeMappingEntry,
    TreeNode,
)


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


def _validate_field_value(field: TreeField, raw_value: Any) -> TreeField:
    if field.meta.required and raw_value in (None, ""):
        return replace(field, value=raw_value, error="This field is required")

    try:
        coerced = coerce_form_value(field.type, raw_value)
        result = load_atomic(field.type, coerced)

        if result is UNHANDLED:
            return replace(field, value=raw_value, error=None)

        return replace(field, value=raw_value, error=None)
    except Exception as e:
        return replace(field, value=raw_value, error=str(e))


def _validate_node(node: TreeNode, flat: dict[str, Any], prefix: str = "") -> TreeNode:
    node_prefix = prefix
    if node.name:
        node_prefix = f"{prefix}.{node.name}" if prefix else node.name

    fields: list[TreeField] = []
    children: list[TreeNode] = []
    lists: list[TreeList] = []
    mappings: list[TreeMapping] = []
    errors = 0

    for field in node.fields:
        key = f"{node_prefix}.{field.name}" if node_prefix else field.name

        if _is_bool_type(field.type):
            raw_value = flat.get(key)
        else:
            raw_value = flat.get(key, field.value)

        validated = _validate_field_value(field, raw_value)
        fields.append(validated)

        if validated.error:
            errors += 1

    for child in node.children:
        validated_child = _validate_node(child, flat, node_prefix)
        children.append(validated_child)
        errors += validated_child.errors

    for tree_list in node.lists:
        prefix_for_list = _child_prefix(node_prefix, tree_list.name)
        row_ids = _collect_row_ids(flat, prefix_for_list)

        list_entries: list[TreeListEntry] = []

        for row_id in row_ids:
            row_prefix = f"{prefix_for_list}.{row_id}"
            validated_item: TreeField | TreeNode

            if isinstance(tree_list.item_schema, TreeField):
                value_key = f"{row_prefix}.value"
                raw_value = (
                    flat.get(value_key)
                    if _is_bool_type(tree_list.item_schema.type)
                    else flat.get(value_key, tree_list.item_schema.value)
                )
                validated_item = _validate_field_value(
                    tree_list.item_schema,
                    raw_value,
                )
                if validated_item.error:
                    errors += 1

            elif isinstance(tree_list.item_schema, TreeNode):
                validated_item = _validate_node(tree_list.item_schema, flat, row_prefix)
                errors += validated_item.errors

            else:
                raise RuntimeError("List missing item schema")

            list_entries.append(TreeListEntry(name=row_id, value=validated_item))

        lists.append(
            TreeList(
                name=tree_list.name,
                meta=tree_list.meta,
                entries=list_entries,
                item_schema=tree_list.item_schema,
            )
        )

    for mapping in node.mappings:
        prefix_for_mapping = _child_prefix(node_prefix, mapping.name)
        row_ids = _collect_row_ids(flat, prefix_for_mapping)

        mapping_entries: list[TreeMappingEntry] = []

        for row_id in row_ids:
            row_prefix = f"{prefix_for_mapping}.{row_id}"

            raw_key = flat.get(f"{row_prefix}.key")
            validated_key = _validate_field_value(mapping.key_schema, raw_key)

            validated_value: TreeField | TreeNode

            if isinstance(mapping.value_schema, TreeField):
                value_key = f"{row_prefix}.value"
                raw_value = (
                    flat.get(value_key)
                    if _is_bool_type(mapping.value_schema.type)
                    else flat.get(value_key, mapping.value_schema.value)
                )
                validated_value = _validate_field_value(
                    mapping.value_schema,
                    raw_value,
                )
                if validated_value.error:
                    errors += 1

            elif isinstance(mapping.value_schema, TreeNode):
                validated_value = _validate_node(mapping.value_schema, flat, row_prefix)
                errors += validated_value.errors

            else:
                raise RuntimeError("Mapping missing value schema")

            if validated_key.error:
                errors += 1

            mapping_entries.append(
                TreeMappingEntry(
                    name=row_id,
                    key=validated_key,
                    value=validated_value,
                )
            )

        mappings.append(
            TreeMapping(
                name=mapping.name,
                meta=mapping.meta,
                entries=mapping_entries,
                key_schema=mapping.key_schema,
                value_schema=mapping.value_schema,
            )
        )

    return TreeNode(
        name=node.name,
        meta=node.meta,
        fields=fields,
        children=children,
        mappings=mappings,
        lists=lists,
        errors=errors,
    )


def validate(tree: TreeNode, flat: dict[str, Any]) -> TreeNode:
    return _validate_node(tree, flat)
