import socket
from pathlib import Path

from bussdcc.service import Service
from bussdcc.context import ContextProtocol

from bussdcc_framework import message


class SystemIdentityService(Service):
    name = "system_identity"

    def start(self, ctx: ContextProtocol) -> None:
        hostname = socket.gethostname()
        model = self._read("/proc/device-tree/model")
        serial = self._cpuinfo_field("Serial")

        ctx.emit(
            message.SystemIdentityEvent(hostname=hostname, model=model, serial=serial)
        )

    def _read(self, path: str) -> str | None:
        try:
            return Path(path).read_text().strip("\x00\n")
        except Exception:
            return None

    def _cpuinfo_field(self, key: str) -> str | None:
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.startswith(key):
                    return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return None
