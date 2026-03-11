from bussdcc import Process, ContextProtocol, Event, Message
from bussdcc import message as bussdcc_message
from bussdcc_framework import message


class SystemIdentityProcess(Process):
    name = "system_identity"

    def handle_event(self, ctx: ContextProtocol, evt: Event[Message]) -> None:
        payload = evt.payload

        if isinstance(payload, bussdcc_message.RuntimeBooted):
            ctx.state.set("runtime.version", payload.version)

        elif isinstance(payload, message.FrameworkBooted):
            ctx.state.set("framework.version", payload.version)

        elif isinstance(payload, message.SystemIdentityEvent):
            ctx.state.set("system.identity", payload)
