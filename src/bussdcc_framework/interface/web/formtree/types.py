from __future__ import annotations
from dataclasses import Field, dataclass
from datetime import date, datetime, time
from enum import Enum
from types import MappingProxyType, UnionType
from typing import Any, Literal, Union, get_args, get_origin


def _unwrap_optional(tp: object) -> object:
    origin = get_origin(tp)
    args = get_args(tp)

    if origin in (Union, UnionType):
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return non_none[0]

    return tp


def _enum_type(tp: object) -> type[Enum] | None:
    if isinstance(tp, type) and issubclass(tp, Enum):
        return tp
    return None


def _field_shape(
    tp: object,
    value: Any | None,
) -> tuple[str, list[str] | None, Any | None]:
    base_tp = _unwrap_optional(tp)
    origin = get_origin(base_tp)
    args = get_args(base_tp)

    enum_tp = _enum_type(base_tp)

    if origin is Literal:
        return "select", [str(v) for v in args], value

    if enum_tp is not None:
        if isinstance(value, Enum):
            value = value.value
        return "select", [str(member.value) for member in enum_tp], value

    if base_tp in (int, float):
        return "number", None, value

    if base_tp is bool:
        return "checkbox", None, value

    if base_tp is date:
        return "date", None, value

    if base_tp is time:
        return "time", None, value

    if base_tp is datetime:
        return "datetime-local", None, value

    return "text", None, value


@dataclass(slots=True, frozen=True)
class FieldMetadata:
    label: str
    group: str = "General"
    required: bool = False
    help: str | None = None
    min: int | float | None = None
    max: int | float | None = None
    step: int | float | None = None

    @staticmethod
    def from_field(f: Field[object]) -> "FieldMetadata":
        meta: MappingProxyType[Any, Any] = f.metadata

        return FieldMetadata(
            label=meta.get("label", f.name),
            group=meta.get("group", "General"),
            required=meta.get("required", False),
            help=meta.get("help"),
            min=meta.get("min"),
            max=meta.get("max"),
            step=meta.get("step"),
        )


@dataclass(slots=True, frozen=True)
class TreeField:
    name: str
    type: object
    meta: FieldMetadata
    value: Any | None = None
    input_type: str | None = None
    options: list[str] | None = None

    @staticmethod
    def create(
        name: str,
        type: object,
        value: Any | None = None,
        *,
        label: str | None = None,
        required: bool = False,
        help: str | None = None,
        min: int | float | None = None,
        max: int | float | None = None,
        step: int | float | None = None,
    ) -> "TreeField":
        meta = FieldMetadata(
            label=label or name,
            required=required,
            help=help,
            min=min,
            max=max,
            step=step,
        )

        input_type, options, value = _field_shape(type, value)

        return TreeField(
            name=name,
            type=type,
            meta=meta,
            value=value,
            input_type=input_type,
            options=options,
        )

    @staticmethod
    def from_field(f: Field[object], value: Any | None = None) -> "TreeField":
        meta = FieldMetadata.from_field(f)
        input_type, options, value = _field_shape(f.type, value)

        return TreeField(
            name=f.name,
            type=f.type,
            meta=meta,
            value=value,
            input_type=input_type,
            options=options,
        )


@dataclass(slots=True, frozen=True)
class TreeMappingEntry:
    name: str
    key: TreeField
    value: TreeField | TreeNode


@dataclass(slots=True, frozen=True)
class TreeMapping:
    name: str
    meta: FieldMetadata
    entries: list[TreeMappingEntry]
    key_schema: TreeField
    value_schema: TreeField | TreeNode

    @property
    def prototype(self) -> TreeMappingEntry:
        return TreeMappingEntry(
            name="__name__",
            key=self.key_schema,
            value=self.value_schema,
        )


@dataclass(slots=True, frozen=True)
class TreeListEntry:
    name: str
    value: TreeField | TreeNode


@dataclass(slots=True, frozen=True)
class TreeList:
    name: str
    meta: FieldMetadata
    entries: list[TreeListEntry]
    item_schema: TreeField | TreeNode

    @property
    def prototype(self) -> TreeListEntry:
        return TreeListEntry(
            name="__name__",
            value=self.item_schema,
        )


@dataclass(slots=True, frozen=True)
class TreeNode:
    name: str | None
    meta: FieldMetadata
    fields: list[TreeField]
    children: list["TreeNode"]
    mappings: list[TreeMapping]
    lists: list[TreeList]
