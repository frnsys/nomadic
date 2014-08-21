from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO

from nomadic.demon import logger
from nomadic import searcher

import os
import sys, logging

import html2text
h = html2text.HTML2Text()

class Server():
    def __init__(self, index, builder, port):
        self.index = index;
        self.builder = builder;
        self.port = port

        self.app = Flask(__name__,
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')

        self.socketio = SocketIO(self.app)
        self.build_routes()

        # To log errors to stdout.
        # Can't really use Flask's debug w/ the websocket lib,
        # but this accomplishes the same thing.
        sh = logging.StreamHandler(sys.stdout)
        self.app.logger.addHandler(sh)

    def start(self):
        logger.debug('Starting the Nomadic server...')
        self.socketio.run(self.app, port=self.port)

    def refresh_clients(self):
        self.socketio.emit('refresh')

    def build_routes(self):
        @self.app.route('/<path:note_path>')
        def note(note_path):
            note_path = '/' + note_path

            # Convert to build path if appropriate.
            if note_path.endswith(('.md', '.html')) and '.build' not in note_path:
                note_path, _ = self.builder.build_path_for_note_path(note_path)

            with open(note_path, 'r') as note:
                content = note.read()
            return content

        @self.app.route('/search', methods=['POST'])
        def search():
            q = request.form['query']
            results = searcher.search(q, self.index, html=True)
            return render_template('results.html', results=results)

        @self.app.route('/new')
        def new():
            return render_template('editor.html')

        @self.app.route('/convert', methods=['POST'])
        def convert():
            """
            Convert HTML to Markdown.
            """
            html = request.form['html']
            md = h.handle(html)
            return md

        @self.socketio.on('connect')
        def on_connect():
            """
            This seems necessary to get
            the SocketIO emitting working properly...
            """
            logger.debug('User connected.')
