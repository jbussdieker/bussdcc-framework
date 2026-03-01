from flask import Flask
from flask_socketio import SocketIO

from bussdcc.context import ContextProtocol


class FlaskApp(Flask):
    ctx: ContextProtocol
    socketio: SocketIO
