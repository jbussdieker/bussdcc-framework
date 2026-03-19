from typing import Dict, Optional
from types import FrameType
import signal

from bussdcc import message

from .runtime import Runtime


class SignalRuntime(Runtime):
    """
    Threaded runtime supervised by POSIX signals.
    """

    SIGNAL_ACTIONS: Dict[int, str] = {
        int(signal.SIGINT): "shutdown",
        int(signal.SIGTERM): "shutdown",
        int(signal.SIGHUP): "reload",
        int(signal.SIGUSR1): "user1",
        int(signal.SIGUSR2): "user2",
    }

    def _signal_handler(self, signum: int, frame: Optional[FrameType]) -> None:
        action = self.SIGNAL_ACTIONS.get(signum)

        if action == "shutdown":
            # Thread-safe: shutdown() only sets state and events
            self.shutdown(signal.strsignal(signum))
        elif action == "reload":
            self.ctx.emit(message.SystemReload())
        elif action:
            self.ctx.emit(message.SystemSignal(signal=signum, action=action))

    def _on_boot(self) -> None:
        super()._on_boot()

        self._prev_handlers = {}
        for signum in self.SIGNAL_ACTIONS:
            self._prev_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, self._signal_handler)

    def _on_shutdown(self, reason: Optional[str] = None) -> None:
        try:
            for signum, handler in self._prev_handlers.items():
                signal.signal(signum, handler)
        finally:
            super()._on_shutdown(reason)
