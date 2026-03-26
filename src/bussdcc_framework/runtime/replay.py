from bussdcc.runtime.replay import ReplayRuntime as KernelReplayRuntime

from .base import FrameworkRuntimeBase


class ReplayRuntime(FrameworkRuntimeBase, KernelReplayRuntime):
    pass
