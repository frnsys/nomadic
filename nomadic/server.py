from flask import Flask, render_template, request, jsonify
from flask.ext.socketio import SocketIO

from nomadic.demon import logger
from nomadic import searcher

import os
import shutil
import urllib
from datetime import datetime
import sys, logging

import html2text
import lxml.html
from lxml.etree import tostring

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

    def _rewrite_link(self, resources_path):
        """
        Creates a link rewriting func
        for a particular resource path.
        """
        def rewriter(link):
            # If the link is an external image...
            if link.startswith('http') and link.endswith(('.jpg', '.jpeg', '.gif', '.png')):
                if not os.path.exists(resources_path):
                    os.makedirs(resources_path)

                # Extract the extension,
                # and create a filename.
                ext = link.split('/')[-1].split('.')[-1]
                filename = str(hash(link)) + '.' + ext

                save_path = os.path.join(resources_path, filename)

                # Download the file if it doesn't exist.
                if not os.path.exists(save_path):
                    filename, _ = urllib.urlretrieve(link, save_path)

                # Return as a relative filepath.
                return save_path.replace(self.index.notes_path, '')
            return link
        return rewriter

    def build_routes(self):
        @self.app.route('/<path:note_path>')
        def note(note_path):
            note_path = '/' + note_path

            # Convert to build path if appropriate.
            if note_path.endswith(('.md', '.html')):
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
            # A unique default title to save without conflicts.
            default_title = datetime.utcnow()
            return render_template('editor.html', notebooks=self.index.notebooks(), title=default_title)

        @self.app.route('/save', methods=['POST'])
        def save():
            title = request.form['title']
            title_ = request.form['prev[title]']

            notebook = request.form['notebook']
            notebook_ = request.form['prev[notebook]']

            resources = os.path.join(notebook, '_resources', title, '')

            # If the title or notebook has changed,
            # remove the old one and move the
            # resources directory (if it exists).
            if title != title_ or notebook != notebook_:
                path_ = os.path.join(notebook_, title_ + '.html')
                os.remove(path_)

                resources_ = os.path.join(notebook_, '_resources', title_, '')
                if os.path.exists(resources_):
                    shutil.move(resources_, resources)

            html = request.form['html']
            path = os.path.join(notebook, title + '.html')

            html_ = lxml.html.fromstring(html)
            html_.rewrite_links(self._rewrite_link(resources))
            html = tostring(html_, method='html')

            with open(path, 'w') as note:
                note.write(html)

            return jsonify({
                'path': path
            })

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

