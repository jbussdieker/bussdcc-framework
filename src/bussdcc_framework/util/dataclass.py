from typing import Any, Type, get_origin, get_args, Literal, Union
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

        origin = get_origin(f.type)
        args = get_args(f.type)

        if origin is list and args and is_dataclass(args[0]) and value is not None:
            value = [build_dataclass(args[0], v) for v in value]
        elif (
            origin is dict
            and args
            and args[0] is str
            and is_dataclass(args[1])
            and value is not None
        ):
            value = {k: build_dataclass(args[1], v) for k, v in value.items()}
        else:
            value = _coerce(f.type, value)

        kwargs[f.name] = value

    if isinstance(cls, type):
        return cls(**kwargs)
