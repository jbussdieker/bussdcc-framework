from typing import Iterable
from datetime import datetime
from pathlib import Path
import json

from bussdcc.io import EventSourceProtocol

from bussdcc.event import Event
from bussdcc.message import Message


class JsonlSource(EventSourceProtocol):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.start_at = None

    def __iter__(self) -> Iterable[Event[Message]]:
        files = sorted(self.root.rglob("*.jsonl"))
        for file in files:
            with file.open() as f:
                for line in f:
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"{file}: {e}")
                        continue
                    evt_time = datetime.fromisoformat(record["time"])
                    if self.start_at and evt_time < self.start_at:
                        continue
                    if not "key" in record:
                        continue  # old format
                    message_cls = Message.resolve(record["key"])
                    yield Event(time=evt_time, payload=message_cls(**record["data"]))
