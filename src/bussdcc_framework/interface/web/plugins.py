from typing import Iterable, Any
from importlib.metadata import entry_points

from bussdcc import ContextProtocol

from .base import FlaskApp
from .protocol import WebPlugin

ENTRYPOINT_GROUP = "bussdcc_framework.web"
PluginSpec = str | WebPlugin


def _load_entrypoint_plugin(name: str) -> WebPlugin:
    matches = entry_points().select(group=ENTRYPOINT_GROUP, name=name)
    ep = next(iter(matches), None)

    if ep is None:
        raise RuntimeError(f"Unknown web plugin: {name}")

    try:
        obj: Any = ep.load()
    except Exception as e:
        raise RuntimeError(f"Failed to load web plugin {name!r}: {e}") from e

    if not isinstance(obj, WebPlugin):
        raise RuntimeError(
            f"Web plugin ignored: {name}: object does not implement WebPlugin"
        )

    return obj


def _resolve_plugin(spec: PluginSpec) -> WebPlugin:
    if isinstance(spec, str):
        return _load_entrypoint_plugin(spec)
    return spec


def resolve_plugins(
    plugins: Iterable[PluginSpec] | None = None,
) -> list[WebPlugin]:
    seen: set[str] = set()
    resolved: list[WebPlugin] = []

    if plugins is None:
        return resolved

    for spec in plugins:
        plugin = _resolve_plugin(spec)

        if plugin.name in seen:
            continue

        resolved.append(plugin)
        seen.add(plugin.name)

    return resolved


def init_plugins(
    app: FlaskApp,
    ctx: ContextProtocol,
    plugins: Iterable[WebPlugin] | None = None,
) -> None:
    if plugins is None:
        return

    for plugin in plugins:
        plugin.init_app(app, ctx)
