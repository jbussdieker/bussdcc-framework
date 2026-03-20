from typing import Any, get_args, get_origin, Literal, Union
from datetime import date, time, datetime
from enum import Enum
from types import UnionType


def unwrap_optional(tp: Any) -> Any:
    origin = get_origin(tp)
    args = get_args(tp)

    if origin in (Union, UnionType):
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return non_none[0]

    return tp


def coerce_form_value(tp: Any, raw: Any) -> Any:
    tp = unwrap_optional(tp)

    if tp is bool:
        return raw in ("on", "true", "1", "yes", True)

    if raw == "":
        if tp is str:
            return ""
        return None

    if raw is None:
        return None

    origin = get_origin(tp)

    if origin is Literal:
        return raw

    if isinstance(tp, type) and issubclass(tp, Enum):
        return raw

    if tp is int:
        return int(raw)

    if tp is float:
        return float(raw)

    if tp in (date, time, datetime):
        return raw

    return raw
