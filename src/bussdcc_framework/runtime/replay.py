import traceback
from typing import Optional

from bussdcc.runtime.replay import ReplayRuntime as Base
from bussdcc.io import EventSinkProtocol
from bussdcc.event import Event
from bussdcc.message import Message, Severity

from .. import message, __version__ as version


class ReplayRuntime(Base):
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
                if evt.payload.severity >= Severity.ERROR:
                    continue

                self.ctx.emit(
                    message.SinkHandlerError(
                        sink=type(sink).__name__,
                        error=repr(e),
                        evt=evt,
                        traceback=traceback.format_exc(),
                    )
                )

        super()._dispatch(evt)

    def shutdown(self, reason: Optional[str] = None) -> None:
        self.ctx.emit(message.FrameworkShuttingDown(version=version, reason=reason))

        try:
            super().shutdown(reason)
        finally:
            for sink in self._sinks:
                try:
                    sink.stop()
                except Exception:
                    pass

    def add_sink(self, sink: EventSinkProtocol) -> None:
        if self._booted:
            raise RuntimeError("Cannot add sinks after boot")
        self._sinks.append(sink)
