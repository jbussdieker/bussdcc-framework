from typing import Iterator
from datetime import datetime
from pathlib import Path
from importlib import import_module
import json

from bussdcc import Event, Message
from bussdcc.io import EventSourceProtocol

from bussdcc_framework.codec import load_value


class JsonlSource(EventSourceProtocol):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.start_at = None

    def __iter__(self) -> Iterator[Event[Message]]:
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

                    if not "type" in record:
                        continue  # invalid format

                    message_type = record["type"]
                    module_path, object_name = message_type.split(":", 2)
                    module = import_module(module_path)
                    message_cls = getattr(module, object_name)

                    yield Event(
                        time=evt_time,
                        payload=load_value(message_cls, record["data"]),
                    )
