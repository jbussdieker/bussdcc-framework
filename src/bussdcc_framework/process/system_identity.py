from bussdcc.process import Process
from bussdcc.context import ContextProtocol
from bussdcc.event import Event
from bussdcc.events import EventSchema
from bussdcc import events as runtime_events

from bussdcc_framework import events


class SystemIdentityProcess(Process):
    name = "system_identity"

    def handle_event(self, ctx: ContextProtocol, evt: Event[EventSchema]) -> None:
        payload = evt.payload

        if isinstance(payload, runtime_events.RuntimeBooted):
            ctx.state.set("runtime.version", payload.version)

        elif isinstance(payload, events.FrameworkBooted):
            ctx.state.set("framework.version", payload.version)

        elif isinstance(payload, events.SystemIdentityEvent):
            ctx.state.set("system.identity", payload)
