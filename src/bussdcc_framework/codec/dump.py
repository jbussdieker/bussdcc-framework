from typing import Any, Callable
from dataclasses import fields, is_dataclass
from datetime import date, time, datetime
from enum import Enum
from pathlib import Path
from uuid import UUID

from .base import UNHANDLED

DumpFallback = Callable[[Any], Any]


def dump_value(obj: Any, fallback: DumpFallback | None = None) -> Any:
    if isinstance(obj, dict):
        return {k: dump_value(v, fallback=fallback) for k, v in obj.items()}

    if isinstance(obj, list):
        return [dump_value(v, fallback=fallback) for v in obj]

    if isinstance(obj, tuple):
        return [dump_value(v, fallback=fallback) for v in obj]

    if isinstance(obj, set):
        return [dump_value(v, fallback=fallback) for v in obj]

    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, UUID):
        return str(obj)

    if is_dataclass(obj) and not isinstance(obj, type):
        return {
            f.name: dump_value(getattr(obj, f.name), fallback=fallback)
            for f in fields(obj)
        }

    if isinstance(obj, type):
        return f"{obj.__module__}:{obj.__qualname__}"

    if fallback is not None:
        alt = fallback(obj)
        if alt is not UNHANDLED:
            return dump_value(alt, fallback=fallback)

    raise TypeError(f"{type(obj)} not serializable")
