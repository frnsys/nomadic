import sys
import logging
from flask import Flask
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

        # log to stdout
        sh = logging.StreamHandler(sys.stdout)
        self.app.logger.addHandler(sh)

    def start(self):
        self.app.logger.debug('starting the nomadic server...')
        self.app.run(port=self.port)
