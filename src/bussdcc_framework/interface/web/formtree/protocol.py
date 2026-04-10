from typing import Protocol

from bussdcc_framework.metadata import FieldRef

from .types import FieldOption


class RefResolver(Protocol):
    def resolve(
        self, ref: FieldRef, field_type: object
    ) -> list[FieldOption] | None: ...
