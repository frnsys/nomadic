import threading

from flask import Flask, render_template, jsonify
from flask.ext.socketio import SocketIO

from nomadic.demon import logger
from nomadic import searcher

class Server():
    def __init__(self, index, builder):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.app.config['DEBUG'] = True

        self.app = Flask(__name__,
                static_folder='static',
                static_url_path='',
                template_folder='templates')

        self.socketio = SocketIO(self.app)
        self.build_routes()

    def start(self):
        logger.debug('Starting the Nomadic server...')
        self.socketio.run(self.app, port=9137)

    def refresh_clients(self):
        self.socketio.emit('refresh')

    def build_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/search', methods=['POST'])
        def search():
            q = request.form['query']
            searcher.search(q, self.index)
            return jsonify()

        @self.socketio.on('connect')
        def on_connect():
            """
            This seems necessary to get
            the SocketIO emitting working properly...
            """
            logger.debug('User connected.')
