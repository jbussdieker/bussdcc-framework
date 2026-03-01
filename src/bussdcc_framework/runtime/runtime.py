import traceback
from typing import Optional

from bussdcc.runtime import SignalRuntime
from bussdcc.event import Event
from bussdcc.message import Message

from bussdcc_framework import message, __version__ as version

from .sink import EventSinkProtocol


class Runtime(SignalRuntime):
    def __init__(self) -> None:
        super().__init__()
        self._sinks: list[EventSinkProtocol] = []

    def boot(self) -> None:
        for sink in self._sinks:
            sink.start(self.ctx)
        super().boot()
        self.ctx.emit(message.FrameworkBooted(version=version))

    def _dispatch(self, evt: Event[Message]) -> None:
        for sink in self._sinks:
            try:
                sink.handle(evt)
            except Exception as e:
                print(repr(e))
                print(traceback.format_exc())
                # TODO: self.ctx.emit(message.SinkHandlerError())

    def shutdown(self, reason: Optional[str] = None) -> None:
        self.ctx.emit(message.FrameworkShuttingDown(version=version, reason=reason))
        super().shutdown(reason)

    def add_sink(self, sink: EventSinkProtocol) -> None:
        if self._booted:
            raise RuntimeError("Cannot add sinks after boot")
        self._sinks.append(sink)
