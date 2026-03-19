import json
from typing import Any

from .codec import dump_value


def to_jsonable(obj: Any) -> Any:
    return dump_value(obj)


def dumps(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault("separators", (",", ":"))
    return json.dumps(to_jsonable(obj), **kwargs)


def loads(s: str, **kwargs: Any) -> Any:
    return json.loads(s, **kwargs)
