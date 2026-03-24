from dataclasses import Field, dataclass
from types import MappingProxyType
from typing import Any


@dataclass(slots=True, frozen=True)
class FieldRef:
    kind: str | None = None
    type_: str | None = None
    protocol: str | None = None


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

    @staticmethod
    def from_field(f: Field[object]) -> "FieldMetadata":
        meta: MappingProxyType[Any, Any] = f.metadata
        raw_ref = meta.get("ref")

        ref = None
        if isinstance(raw_ref, dict):
            ref = FieldRef(
                kind=raw_ref.get("kind"),
                type_=raw_ref.get("type"),
                protocol=raw_ref.get("protocol"),
            )

        return FieldMetadata(
            label=meta.get("label", f.name),
            group=meta.get("group", "General"),
            required=meta.get("required", False),
            help=meta.get("help"),
            min=meta.get("min"),
            max=meta.get("max"),
            step=meta.get("step"),
            ref=ref,
        )
