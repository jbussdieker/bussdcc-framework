from typing import Any
import json

from bussdcc.event import Event
from bussdcc.events import EventSchema
from bussdcc.context import ContextProtocol

from .protocol import EventSinkProtocol


class ConsoleSink(EventSinkProtocol):
    def start(self, ctx: ContextProtocol) -> None:
        pass

    def stop(self) -> None:
        pass

    def handle(self, evt: Event[object]) -> None:
        if not evt.time:
            return

        payload = evt.payload
        if not isinstance(payload, EventSchema):
            print("Invalid event", payload)
            return

        record = {
            "time": evt.time.isoformat(),
            "name": payload.name,
            "data": self.transform(evt),
        }

        line = json.dumps(record, separators=(",", ":"))
        print(line)

    def transform(self, evt: Event[object]) -> Any:
        """
        Override to customize JSON output.

        Must return a JSON-serializable dict.
        Should not mutate evt.
        """
        if hasattr(evt.payload, "to_dict"):
            return evt.payload.to_dict()
