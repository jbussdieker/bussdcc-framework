from datetime import datetime, date, time
from dataclasses import is_dataclass, fields
from enum import Enum
from pathlib import Path
import json
from typing import Any


def to_jsonable(obj: Any) -> Any:
    """Convert Python objects into JSON-serializable structures."""

    # Fast path for common container types
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]

    # Primitive JSON types
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Framework-supported objects
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, Path):
        return str(obj)

    if is_dataclass(obj):
        if isinstance(obj, type):
            return f"{obj.__module__}:{obj.__qualname__}"

        return {f.name: to_jsonable(getattr(obj, f.name)) for f in fields(obj)}

    raise TypeError(f"{type(obj)} not JSON serializable")


def dumps(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault("separators", (",", ":"))
    return json.dumps(to_jsonable(obj), **kwargs)


def loads(s: str, **kwargs: Any) -> Any:
    return json.loads(s, **kwargs)
