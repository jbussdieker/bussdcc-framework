from flask import current_app

from bussdcc import ContextProtocol, Message

from .base import FlaskApp


def current_ctx() -> ContextProtocol:
    if not isinstance(current_app, FlaskApp):
        raise RuntimeError("Not inside FlaskApp context")
    return current_app.ctx


def emit(message: Message) -> None:
    current_ctx().emit(message)
