from typing import Any

from bussdcc import Event, Message, ContextProtocol
from bussdcc.io import EventSinkProtocol
from bussdcc_framework import json as framework_json


class ConsoleSink(EventSinkProtocol):
    def start(self, ctx: ContextProtocol) -> None:
        pass

    def stop(self) -> None:
        pass

    def json_fallback(self, obj: Any) -> Any:
        return framework_json.UNHANDLED

    def handle(self, evt: Event[Message]) -> None:
        if not evt.time:
            return

        record = {
            "time": evt.time,
            "type": type(evt.payload),
            "data": self.transform(evt),
        }

        try:
            line = framework_json.dumps(record, fallback=self.json_fallback)
        except Exception:
            line = repr(evt)

        print(line)

    def transform(self, evt: Event[Message]) -> Any:
        return evt.payload
