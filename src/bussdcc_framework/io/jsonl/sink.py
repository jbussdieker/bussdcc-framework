from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, TextIO
import threading

from bussdcc import Event, Message, ContextProtocol
from bussdcc.io import EventSinkProtocol
from bussdcc_framework import json as framework_json


class JsonlSink(EventSinkProtocol):
    def __init__(
        self,
        root: str | Path,
        interval: float = 600.0,
    ):
        self.root = Path(root)
        self.interval = timedelta(seconds=interval)

        self._file: TextIO | None = None
        self._current_segment_start: datetime | None = None
        self._lock = threading.Lock()

    def start(self, ctx: ContextProtocol) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def stop(self) -> None:
        if self._file:
            self._file.close()
            self._file = None

    def json_fallback(self, obj: Any) -> Any:
        return framework_json.UNHANDLED

    def handle(self, evt: Event[Message]) -> None:
        if not evt.time:
            return

        segment_start = self._segment_start(evt.time)

        with self._lock:
            if segment_start != self._current_segment_start:
                self._rotate(segment_start)

            record = {
                "time": evt.time,
                "type": type(evt.payload),
                "data": self.transform(evt),
            }

            line = framework_json.dumps(record, fallback=self.json_fallback)
            assert self._file is not None
            self._file.write(line + "\n")

    def transform(self, evt: Event[Message]) -> Any:
        return evt.payload

    def _segment_start(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        interval_seconds = self.interval.total_seconds()
        timestamp = dt.timestamp()
        bucket = int(timestamp // interval_seconds) * interval_seconds
        return datetime.fromtimestamp(bucket, tz=dt.tzinfo)

    def _rotate(self, segment_start: datetime) -> None:
        if self._file:
            self._file.close()

        self._current_segment_start = segment_start

        day_dir = self.root / segment_start.strftime("%Y-%m-%d")
        day_dir.mkdir(parents=True, exist_ok=True)

        filename = segment_start.strftime("%H-%M-%S.jsonl")
        path = day_dir / filename

        self._file = path.open("a", buffering=1)
