from dataclasses import is_dataclass, fields, MISSING
from typing import Any, Optional, TypeAlias, Literal, get_origin, get_args, Union
from enum import Enum
from types import UnionType

from bussdcc_framework.metadata import FieldMetadata

from .protocol import RefResolver
from .types import (
    FieldOption,
    TreeNode,
    TreeField,
    TreeMapping,
    TreeMappingEntry,
    TreeListEntry,
    TreeList,
)

TreeValue: TypeAlias = TreeField | TreeNode


def _unwrap_optional(tp: object) -> object:
    origin = get_origin(tp)
    args = get_args(tp)

    if origin in (Union, UnionType):
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return non_none[0]

    return tp


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
    tp = _unwrap_optional(tp)
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


def _resolve_ref_options(
    meta: FieldMetadata | None,
    field_type: object,
    ref_resolver: RefResolver | None,
) -> list[FieldOption] | None:
    if meta is None or meta.ref is None or ref_resolver is None:
        return None

    return ref_resolver.resolve(meta.ref, field_type)


def build(
    obj: Any,
    name: Optional[str] = None,
    meta: Optional[FieldMetadata] = None,
    ref_resolver: RefResolver | None = None,
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
            item_meta = field_meta.item_meta or FieldMetadata(label="Value")

            list_item_schema: TreeValue
            if is_dataclass(subtype):
                list_item_schema = build(
                    subtype,
                    "value",
                    meta=item_meta,
                    ref_resolver=ref_resolver,
                )
            else:
                list_item_schema = TreeField.create(
                    "value",
                    subtype,
                    meta=item_meta,
                    ref_options=_resolve_ref_options(
                        item_meta,
                        subtype,
                        ref_resolver,
                    ),
                )

            if value:
                for i, item in enumerate(value):
                    list_entry_value: TreeValue
                    if is_dataclass(subtype):
                        list_entry_value = build(
                            item,
                            "value",
                            meta=item_meta,
                            ref_resolver=ref_resolver,
                        )
                    else:
                        list_entry_value = TreeField.create(
                            "value",
                            subtype,
                            value=item,
                            meta=item_meta,
                            ref_options=_resolve_ref_options(
                                item_meta,
                                subtype,
                                ref_resolver,
                            ),
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

            key_meta = field_meta.key_meta or FieldMetadata(label="Key")
            value_meta = field_meta.value_meta or FieldMetadata(label="Value")

            mapping_entries: list[TreeMappingEntry] = []

            mapping_value_schema: TreeValue
            if is_dataclass(subtype):
                mapping_value_schema = build(
                    subtype,
                    "value",
                    meta=value_meta,
                    ref_resolver=ref_resolver,
                )
            else:
                mapping_value_schema = TreeField.create(
                    "value",
                    subtype,
                    meta=value_meta,
                    ref_options=_resolve_ref_options(
                        value_meta,
                        subtype,
                        ref_resolver,
                    ),
                )

            key_schema = TreeField.create(
                "key",
                key_type,
                meta=key_meta,
                ref_options=_resolve_ref_options(
                    key_meta,
                    key_type,
                    ref_resolver,
                ),
            )

            if value:
                for i, (k, v) in enumerate(value.items()):
                    mapping_entry_value: TreeValue
                    if is_dataclass(subtype):
                        mapping_entry_value = build(
                            v,
                            "value",
                            meta=value_meta,
                            ref_resolver=ref_resolver,
                        )
                    else:
                        mapping_entry_value = TreeField.create(
                            "value",
                            subtype,
                            value=v,
                            meta=value_meta,
                            ref_options=_resolve_ref_options(
                                value_meta,
                                subtype,
                                ref_resolver,
                            ),
                        )

                    mapping_entries.append(
                        TreeMappingEntry(
                            name=str(i),
                            key=TreeField.create(
                                "key",
                                key_type,
                                value=k,
                                meta=key_meta,
                                ref_options=_resolve_ref_options(
                                    key_meta,
                                    key_type,
                                    ref_resolver,
                                ),
                            ),
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
                build(
                    nested,
                    f.name,
                    meta=FieldMetadata.from_field(f),
                    ref_resolver=ref_resolver,
                )
            )
            continue

        ref_options = None
        if ref_resolver is not None and field_meta.ref is not None:
            ref_options = ref_resolver.resolve(field_meta.ref, f.type)

        node_fields.append(
            TreeField.from_field(
                f,
                value=value,
                meta=field_meta,
                ref_options=ref_options,
            )
        )

    return TreeNode(
        name=name,
        meta=meta,
        fields=node_fields,
        children=node_children,
        mappings=node_mappings,
        lists=node_lists,
    )
