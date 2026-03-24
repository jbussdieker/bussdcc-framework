from dataclasses import is_dataclass, fields, MISSING
from typing import Any, Optional, TypeAlias, Literal, get_origin, get_args
from enum import Enum

from bussdcc_framework.metadata import FieldMetadata

from .types import (
    TreeNode,
    TreeField,
    TreeMapping,
    TreeMappingEntry,
    TreeListEntry,
    TreeList,
)

TreeValue: TypeAlias = TreeField | TreeNode


def _is_supported_mapping_key_type(tp: object) -> bool:
    origin = get_origin(tp)

    if tp in (str, int, float, bool):
        return True

    if origin is Literal:
        return True

    if isinstance(tp, type) and issubclass(tp, Enum):
        return True

    return False


def _detect_container(tp: object) -> tuple[str | None, Any | None, Any | None]:
    origin = get_origin(tp)
    args = get_args(tp)

    if origin in (list, tuple) and args:
        item_tp = args[0]
        if len(args) == 2 and args[1] is Ellipsis:
            item_tp = args[0]
        return "list", None, item_tp

    if origin is dict and len(args) == 2:
        return "dict", args[0], args[1]

    return None, None, None


def build(
    obj: Any, name: Optional[str] = None, meta: Optional[FieldMetadata] = None
) -> TreeNode:
    if not is_dataclass(obj):
        raise TypeError("Expected dataclass")

    is_instance = not isinstance(obj, type)

    node_fields: list[TreeField] = []
    node_children: list[TreeNode] = []
    node_mappings: list[TreeMapping] = []
    node_lists: list[TreeList] = []

    if meta is None:
        meta = FieldMetadata(label=name or "Configuration")

    for f in fields(obj):
        if is_instance:
            value = getattr(obj, f.name)
        else:
            if f.default is not MISSING:
                value = f.default
            elif f.default_factory is not MISSING:
                value = f.default_factory()
            else:
                value = None

        container, key_type, subtype = _detect_container(f.type)
        field_meta = FieldMetadata.from_field(f)

        if container == "list":
            list_entries: list[TreeListEntry] = []

            list_item_schema: TreeValue
            if is_dataclass(subtype):
                list_item_schema = build(
                    subtype, "value", meta=FieldMetadata(label=field_meta.label)
                )
            else:
                list_item_schema = TreeField.create("value", subtype, label="Value")

            if value:
                for i, item in enumerate(value):
                    list_entry_value: TreeValue
                    if is_dataclass(subtype):
                        list_entry_value = build(item, "value")
                    else:
                        list_entry_value = TreeField.create(
                            "value",
                            subtype,
                            value=item,
                            label="Value",
                        )

                    list_entries.append(
                        TreeListEntry(
                            name=str(i),
                            value=list_entry_value,
                        )
                    )

            node_lists.append(
                TreeList(
                    name=f.name,
                    meta=field_meta,
                    entries=list_entries,
                    item_schema=list_item_schema,
                )
            )
            continue

        if container == "dict":
            if not _is_supported_mapping_key_type(key_type):
                raise TypeError(
                    f"Unsupported mapping key type for formtree: {key_type!r}. "
                    "Only str, int, float, bool, Literal, and Enum are supported."
                )

            mapping_entries: list[TreeMappingEntry] = []

            mapping_value_schema: TreeValue
            if is_dataclass(subtype):
                mapping_value_schema = build(
                    subtype, "value", meta=FieldMetadata(label=field_meta.label)
                )
            else:
                mapping_value_schema = TreeField.create(
                    "value",
                    subtype,
                    label="Value",
                )

            key_schema = TreeField.create("key", key_type, label="Key")

            if value:
                for i, (k, v) in enumerate(value.items()):
                    mapping_entry_value: TreeValue
                    if is_dataclass(subtype):
                        mapping_entry_value = build(v, "value")
                    else:
                        mapping_entry_value = TreeField.create(
                            "value",
                            subtype,
                            value=v,
                            label="Value",
                        )

                    mapping_entries.append(
                        TreeMappingEntry(
                            name=str(i),
                            key=TreeField.create("key", key_type, value=k, label="Key"),
                            value=mapping_entry_value,
                        )
                    )

            node_mappings.append(
                TreeMapping(
                    name=f.name,
                    meta=field_meta,
                    entries=mapping_entries,
                    key_schema=key_schema,
                    value_schema=mapping_value_schema,
                )
            )
            continue

        if is_dataclass(f.type):
            nested = value if is_instance else f.type
            node_children.append(
                build(nested, f.name, meta=FieldMetadata.from_field(f))
            )
            continue

        node_fields.append(TreeField.from_field(f, value=value))

    return TreeNode(
        name=name,
        meta=meta,
        fields=node_fields,
        children=node_children,
        mappings=node_mappings,
        lists=node_lists,
    )
