import json
import threading
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, TextIO

from bussdcc.event import Event
from bussdcc.events import EventSchema
from bussdcc.context import ContextProtocol

from .protocol import EventSinkProtocol


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

    def handle(self, evt: Event[object]) -> None:
        if not evt.time:
            return

        payload = evt.payload
        if not isinstance(payload, EventSchema):
            print("Invalid event", payload)
            return

        segment_start = self._segment_start(evt.time)

        with self._lock:
            if segment_start != self._current_segment_start:
                self._rotate(segment_start)

            record = {
                "time": evt.time.isoformat(),
                "name": payload.name,
                "data": self.transform(evt),
            }

            line = json.dumps(record, separators=(",", ":"))
            assert self._file is not None
            self._file.write(line + "\n")

    def transform(self, evt: Event[object]) -> Any:
        """
        Override to customize JSON output.

        Must return a JSON-serializable dict.
        Should not mutate evt.
        """
        if hasattr(evt.payload, "to_dict"):
            return evt.payload.to_dict()

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
