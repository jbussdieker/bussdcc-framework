from typing import Any

from bussdcc import Event, Message, ContextProtocol
from bussdcc.io import EventSinkProtocol
from bussdcc_framework import json as framework_json


class ConsoleSink(EventSinkProtocol):
    def start(self, ctx: ContextProtocol) -> None:
        pass

    def stop(self) -> None:
        pass

    def handle(self, evt: Event[Message]) -> None:
        if not evt.time:
            return

        record = {
            "time": evt.time,
            "type": type(evt.payload),
            "data": self.transform(evt),
        }

        try:
            line = framework_json.dumps(record, separators=(",", ":"))
        except:
            line = repr(evt)

        print(line)

    def transform(self, evt: Event[Message]) -> Any:
        """
        Override to customize JSON output.

        Must return a JSON-serializable dict.
        Should not mutate evt.
        """
        return evt.payload
