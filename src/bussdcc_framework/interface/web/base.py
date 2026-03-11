from flask import Flask
from flask_socketio import SocketIO

from bussdcc import ContextProtocol


class FlaskApp(Flask):
    ctx: ContextProtocol
    socketio: SocketIO
