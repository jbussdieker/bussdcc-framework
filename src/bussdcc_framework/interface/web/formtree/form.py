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


def _coerce_literal_value(options: tuple[Any, ...], raw: Any) -> Any:
    for option in options:
        if raw == option:
            return option

        if isinstance(option, bool):
            if raw in ("true", "1", "on", "yes", True) and option is True:
                return True
            if raw in ("false", "0", "off", "no", False) and option is False:
                return False
            continue

        if str(option) == str(raw):
            return option

    raise ValueError(f"{raw!r} is not one of {options!r}")


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
        return _coerce_literal_value(get_args(tp), raw)

    if isinstance(tp, type) and issubclass(tp, Enum):
        return raw

    if tp is int:
        return int(raw)

    if tp is float:
        return float(raw)

    if tp in (date, time, datetime):
        return raw

    return raw
