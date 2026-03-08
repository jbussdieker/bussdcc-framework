from typing import Any
import json

from bussdcc.event import Event
from bussdcc.message import Message
from bussdcc.context import ContextProtocol
from bussdcc.io import EventSinkProtocol


class ConsoleSink(EventSinkProtocol):
    def start(self, ctx: ContextProtocol) -> None:
        pass

    def stop(self) -> None:
        pass

    def handle(self, evt: Event[Message]) -> None:
        if not evt.time:
            return

        record = {
            "time": evt.time.isoformat(),
            "message": evt.payload._key(),
            "data": self.transform(evt),
        }

        try:
            line = json.dumps(record, separators=(",", ":"))
        except:
            line = repr(evt)

        print(line)

    def transform(self, evt: Event[Message]) -> Any:
        """
        Override to customize JSON output.

        Must return a JSON-serializable dict.
        Should not mutate evt.
        """
        return evt.payload.to_dict() if hasattr(evt.payload, "to_dict") else {}
