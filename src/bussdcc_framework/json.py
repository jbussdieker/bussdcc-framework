import json
from typing import Any

from .codec.dump import dump_value, UNHANDLED, DumpFallback


def to_jsonable(obj: Any, fallback: DumpFallback | None = None) -> Any:
    return dump_value(obj, fallback=fallback)


def dumps(obj: Any, **kwargs: Any) -> str:
    fallback = kwargs.pop("fallback", None)
    kwargs.setdefault("separators", (",", ":"))
    return json.dumps(to_jsonable(obj, fallback=fallback), **kwargs)


def loads(s: str, **kwargs: Any) -> Any:
    return json.loads(s, **kwargs)


def to_json_primitives(obj: Any, fallback: DumpFallback | None = None) -> Any:
    return loads(dumps(obj, fallback=fallback))


__all__ = [
    "UNHANDLED",
    "to_jsonable",
    "to_json_primitives",
    "dumps",
    "loads",
]
