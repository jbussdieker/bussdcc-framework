import traceback
from typing import Optional

from bussdcc import Runtime as KernelRuntime
from bussdcc import Event, Message, Severity, ContextProtocol
from bussdcc.clock import ClockProtocol
from bussdcc.event import EventBusProtocol
from bussdcc.io import EventSinkProtocol
from bussdcc.state import StateStoreProtocol

from .. import message, __version__ as version


def _message_type_name(msg: Message) -> str:
    cls = type(msg)
    return f"{cls.__module__}:{cls.__qualname__}"


class FrameworkRuntimeBase(KernelRuntime):
    def __init__(
        self,
        *,
        clock: Optional[ClockProtocol] = None,
        events: Optional[EventBusProtocol] = None,
        state: Optional[StateStoreProtocol] = None,
    ):
        super().__init__(clock=clock, events=events, state=state)
        self._sinks: list[EventSinkProtocol] = []

    def add_sink(self, sink: EventSinkProtocol) -> None:
        if self.booted:
            raise RuntimeError("Cannot add sinks after boot")
        self._sinks.append(sink)

    def boot(self) -> None:
        for sink in self._sinks:
            sink.start(self.ctx)

        super().boot()
        self.ctx.emit(message.FrameworkBooted(version=version))

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

    def _dispatch(self, evt: Event[Message]) -> None:
        self._dispatch_to_sinks(evt)
        super()._dispatch(evt)
        self._record_runtime_telemetry(evt)

    def _dispatch_to_sinks(self, evt: Event[Message]) -> None:
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

    def _record_runtime_telemetry(self, evt: Event[Message]) -> None:
        self.ctx.state.update(
            "runtime_info.stats.message_count",
            lambda v: (v or 0) + 1,
        )

        if evt.payload.severity >= Severity.ERROR:
            self.ctx.state.update(
                "runtime_info.stats.error_count",
                lambda v: (v or 0) + 1,
            )

        self.ctx.state.update(
            f"runtime_info.severity.{evt.payload.severity.name.lower()}",
            lambda v: (v or 0) + 1,
        )

        self.ctx.state.update(
            f"runtime_info.message_types.{_message_type_name(evt.payload)}",
            lambda v: (v or 0) + 1,
        )
