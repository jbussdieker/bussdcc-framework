from bussdcc.process import Process
from bussdcc.context import ContextProtocol
from bussdcc.event import Event
from bussdcc.message import Message
from bussdcc import message as runtime_message

from bussdcc_framework import message


class SystemIdentityProcess(Process):
    name = "system_identity"

    def handle_event(self, ctx: ContextProtocol, evt: Event[Message]) -> None:
        payload = evt.payload

        if isinstance(payload, runtime_message.RuntimeBooted):
            ctx.state.set("runtime.version", payload.version)

        elif isinstance(payload, message.FrameworkBooted):
            ctx.state.set("framework.version", payload.version)

        elif isinstance(payload, message.SystemIdentityEvent):
            ctx.state.set("system.identity", payload)
