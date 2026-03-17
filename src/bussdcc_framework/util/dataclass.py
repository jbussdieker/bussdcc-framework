from typing import Any, Type, get_origin, get_args, Literal, Union
from enum import Enum
from dataclasses import is_dataclass, fields, MISSING
from datetime import date, time, datetime


def _coerce(tp: Any, value: Any) -> Any:
    if value is None:
        return None

    origin = get_origin(tp)
    args = get_args(tp)

    # Optional[T] / Union[T, None]
    if origin is Union and type(None) in args:
        real_type = next(a for a in args if a is not type(None))
        return _coerce(real_type, value)

    if origin is Literal:
        if value not in args:
            raise ValueError(f"{value!r} not in {args}")
        return value

    if isinstance(tp, type) and issubclass(tp, Enum):
        if isinstance(value, tp):
            return value
        return tp(value)

    if tp is bool:
        return value in ("on", "true", "1", True)

    if tp is int:
        return int(value)

    if tp is float:
        return float(value)

    if tp is date and isinstance(value, str):
        return date.fromisoformat(value)

    if tp is time and isinstance(value, str):
        return time.fromisoformat(value)

    if tp is datetime and isinstance(value, str):
        return datetime.fromisoformat(value)

    return value


def build_dataclass(cls: object | type[object], data: dict[str, Any]) -> Any:
    if not is_dataclass(cls):
        raise TypeError(f"{cls} is not a dataclass")

    kwargs = {}

    for f in fields(cls):
        value = data.get(f.name, MISSING)

        if is_dataclass(f.type) and value is not None and not isinstance(value, dict):
            raise TypeError(f"{f.name} must be a dict")

        if value is MISSING:
            if f.default is not MISSING:
                value = f.default
            elif f.default_factory is not MISSING:
                value = f.default_factory()
            else:
                value = None

        if is_dataclass(f.type):
            value = build_dataclass(f.type, value or {})
            kwargs[f.name] = value
            continue

        origin = get_origin(f.type)
        args = get_args(f.type)

        if origin is list and args and value is not None:
            item_type = args[0]
            if is_dataclass(item_type):
                value = [build_dataclass(item_type, v) for v in value]
            else:
                value = [_coerce(item_type, v) for v in value]

        elif origin is tuple and args and value is not None:
            if len(args) == 2 and args[1] is Ellipsis:
                item_type = args[0]
                if is_dataclass(item_type):
                    value = tuple(build_dataclass(item_type, v) for v in value)
                else:
                    value = tuple(_coerce(item_type, v) for v in value)
            else:
                # fixed-length tuple[T1, T2, ...]
                coerced = []
                for item_type, item_value in zip(args, value):
                    if is_dataclass(item_type):
                        coerced.append(build_dataclass(item_type, item_value))
                    else:
                        coerced.append(_coerce(item_type, item_value))
                value = tuple(coerced)

        elif origin is dict and len(args) == 2 and args[0] is str and value is not None:
            value_type = args[1]
            if is_dataclass(value_type):
                value = {k: build_dataclass(value_type, v) for k, v in value.items()}
            else:
                value = {k: _coerce(value_type, v) for k, v in value.items()}

        else:
            value = _coerce(f.type, value)

        kwargs[f.name] = value

    if isinstance(cls, type):
        return cls(**kwargs)
