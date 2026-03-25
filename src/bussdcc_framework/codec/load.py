from typing import Any, Literal, Union, get_args, get_origin, get_type_hints
from dataclasses import fields, is_dataclass, MISSING
from datetime import date, time, datetime
from enum import Enum
from pathlib import Path
import types

from .base import UNHANDLED


def load_atomic(tp: Any, value: Any) -> Any:
    origin = get_origin(tp)
    args = get_args(tp)

    if origin is Literal:
        if value not in args:
            raise ValueError(f"{value!r} not in {args}")
        return value

    if isinstance(tp, type) and issubclass(tp, Enum):
        if isinstance(value, tp):
            return value
        return tp(value)

    if tp is bool:
        if isinstance(value, bool):
            return value
        if value in ("true", "1", "on", "yes"):
            return True
        if value in ("false", "0", "off", "no"):
            return False
        raise TypeError(f"{tp} requires boolean-like input")

    if tp is str:
        if not isinstance(value, str):
            raise TypeError(f"{tp} requires string input")
        return value

    if tp is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{tp} requires integer input")
        return value

    if tp is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{tp} requires numeric input")
        return float(value)

    if tp is Path:
        if not isinstance(value, (str, Path)):
            raise TypeError(f"{tp} requires path-like input")
        return Path(value)

    if tp is datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError(f"{tp} requires ISO datetime string input")

    if tp is date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise TypeError(f"{tp} requires ISO date string input")

    if tp is time:
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            return time.fromisoformat(value)
        raise TypeError(f"{tp} requires ISO time string input")

    return UNHANDLED


def load_value(tp: Any, value: Any) -> Any:
    origin = get_origin(tp)
    args = get_args(tp)

    if value is None:
        if origin in (Union, types.UnionType) and type(None) in args:
            return None
        raise TypeError(f"None is not valid for {tp!r}")

    if origin in (Union, types.UnionType):
        if type(None) in args:
            real_type = next(a for a in args if a is not type(None))
            return load_value(real_type, value)

        raise TypeError(f"{tp} is not a supported union type")

    atomic = load_atomic(tp, value)
    if atomic is not UNHANDLED:
        return atomic

    if isinstance(tp, type) and is_dataclass(tp):
        if not isinstance(value, dict):
            raise TypeError(f"{tp} requires dict input")

        type_hints = get_type_hints(tp)
        kwargs: dict[str, Any] = {}

        for f in fields(tp):
            field_tp = type_hints.get(f.name, f.type)

            if f.name in value:
                kwargs[f.name] = load_value(field_tp, value[f.name])
                continue

            if f.default is not MISSING:
                kwargs[f.name] = f.default
                continue

            if f.default_factory is not MISSING:
                kwargs[f.name] = f.default_factory()
                continue

            raise TypeError(
                f"Missing required field {f.name!r} for {tp.__module__}:{tp.__qualname__}"
            )

        return tp(**kwargs)

    if origin is list:
        if not isinstance(value, list):
            raise TypeError(f"{tp} requires list input")
        item_tp = args[0]
        return [load_value(item_tp, item) for item in value]

    if origin is tuple:
        if not isinstance(value, (list, tuple)):
            raise TypeError(f"{tp} requires list/tuple input")

        if len(args) == 2 and args[1] is Ellipsis:
            item_tp = args[0]
            return tuple(load_value(item_tp, item) for item in value)

        if len(value) != len(args):
            raise TypeError(f"Expected tuple of length {len(args)}, got {len(value)}")

        return tuple(load_value(item_tp, item) for item_tp, item in zip(args, value))

    if origin is dict:
        if not isinstance(value, dict):
            raise TypeError(f"{tp} requires dict input")

        key_tp, value_tp = args
        return {
            load_value(key_tp, k): load_value(value_tp, v) for k, v in value.items()
        }

    if origin is set:
        if not isinstance(value, list):
            raise TypeError(f"{tp} requires list input")
        item_tp = args[0]
        return {load_value(item_tp, item) for item in value}

    raise TypeError(f"{tp} is not a supported type")
