import sys
import logging
from flask import Flask
from flask.ext.socketio import SocketIO
from nomadic.server.routes import routes


class Server():
    """handles the web interface and
    refreshing of connected clients."""

    def __init__(self, port):
        self.port = port

        self.app = Flask(__name__,
                static_folder='assets/static',
                static_url_path='/static',
                template_folder='assets/templates')
        self.app.register_blueprint(routes)

        self.socketio = SocketIO(self.app)

        # log to stdout
        sh = logging.StreamHandler(sys.stdout)
        self.app.logger.addHandler(sh)

        @self.socketio.on('connect')
        def on_connect():
            """this seems necessary to get
            the SocketIO emitting working properly"""
            pass

    def start(self):
        self.app.logger.debug('starting the nomadic server...')
        self.socketio.run(self.app, port=self.port)

    def refresh_clients(self):
        self.socketio.emit('refresh')
