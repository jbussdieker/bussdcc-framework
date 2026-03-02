from flask import current_app

from bussdcc.context import ContextProtocol
from bussdcc.message import Message

from .base import FlaskApp


def current_ctx() -> ContextProtocol:
    assert isinstance(current_app, FlaskApp)
    return current_app.ctx


def emit(message: Message) -> None:
    current_ctx().emit(message)
