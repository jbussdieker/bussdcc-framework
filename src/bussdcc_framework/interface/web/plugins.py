from typing import Iterable, Any
from importlib.metadata import entry_points

from bussdcc import ContextProtocol

from .base import FlaskApp
from .protocol import WebPlugin

ENTRYPOINT_GROUP = "bussdcc_framework.web"


def _load_entrypoint_plugins() -> Iterable[WebPlugin]:
    for ep in entry_points().select(group=ENTRYPOINT_GROUP):
        try:
            obj: Any = ep.load()
        except Exception as e:
            print(f"Web plugin load failure: {ep.name}: {e}")
            continue

        if isinstance(obj, WebPlugin):
            yield obj
            continue

        print(f"Web plugin ignored: {ep.name}: object does not implement WebPlugin")


def load_plugins(
    app: FlaskApp,
    ctx: ContextProtocol,
    explicit_plugins: Iterable[WebPlugin] | None = None,
) -> None:
    seen: set[str] = set()

    if explicit_plugins is not None:
        for plugin in explicit_plugins:
            if plugin.name in seen:
                continue
            plugin.init_app(app, ctx)
            seen.add(plugin.name)

    for plugin in _load_entrypoint_plugins():
        if plugin.name in seen:
            continue
        plugin.init_app(app, ctx)
        seen.add(plugin.name)
