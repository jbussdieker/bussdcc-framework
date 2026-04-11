from dataclasses import Field, dataclass
from types import MappingProxyType
from typing import Any


@dataclass(slots=True, frozen=True)
class FieldRef:
    kind: str | None = None
    type_: str | None = None
    protocol: str | None = None


def _parse_ref(raw_ref: object) -> FieldRef | None:
    if not isinstance(raw_ref, dict):
        return None

    return FieldRef(
        kind=raw_ref.get("kind"),
        type_=raw_ref.get("type"),
        protocol=raw_ref.get("protocol"),
    )


def _parse_meta(raw: object, *, default_label: str) -> "FieldMetadata | None":
    if not isinstance(raw, dict):
        return None

    return FieldMetadata(
        label=raw.get("label", default_label),
        group=raw.get("group", "General"),
        required=raw.get("required", False),
        help=raw.get("help"),
        min=raw.get("min"),
        max=raw.get("max"),
        step=raw.get("step"),
        ref=_parse_ref(raw.get("ref")),
    )


@dataclass(slots=True, frozen=True)
class FieldMetadata:
    label: str
    group: str = "General"
    required: bool = False
    help: str | None = None
    min: int | float | None = None
    max: int | float | None = None
    step: int | float | None = None
    ref: FieldRef | None = None
    item_meta: "FieldMetadata | None" = None
    key_meta: "FieldMetadata | None" = None
    value_meta: "FieldMetadata | None" = None

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
            ref=_parse_ref(meta.get("ref")),
            item_meta=_parse_meta(meta.get("item_meta"), default_label="Value"),
            key_meta=_parse_meta(meta.get("key_meta"), default_label="Key"),
            value_meta=_parse_meta(meta.get("value_meta"), default_label="Value"),
        )
