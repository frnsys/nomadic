from flask import Flask, render_template, request, jsonify
from flask.ext.socketio import SocketIO

from nomadic.demon import logger
from nomadic import searcher, manager, converter

import os
import shutil
import urllib
from datetime import datetime
import sys, logging

from lxml.html import fromstring, tostring

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
            """
            This downloads externally-hosted images
            to a note's local resources folder and
            rewrites the referencing links to point
            to the local files.
            """
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
            return render_template('editor.html', notebooks=self.index.notebooks, title=default_title)

        @self.app.route('/save', methods=['POST'])
        def save():
            html = request.form['html']

            if html:
                save_as_markdown = request.form['save_as_markdown']
                if save_as_markdown:
                    ext = '.md'
                else:
                    ext = '.html'

                title = request.form['title']
                notebook = request.form['notebook']
                path = os.path.join(notebook, title + ext) 

                title_new = request.form['new[title]']
                notebook_new = request.form['new[notebook]']
                path_new = os.path.join(notebook_new, title_new + ext)

                # If the title or notebook has changed,
                # move the note by updating its path.
                if path != path_new:

                    # Check if the new path exists already.
                    # We don't want to overwrite existing notes.
                    if os.path.exists(path_new):
                        # 409 = Conflict
                        self.app.logger.debug('Note at {0} already exists.'.format(path_new))
                        return 'Note already exists', 409

                    manager.move_note(path, path_new)
                    path = path_new

                resources = manager.note_resources(path, create=True)
                html_ = fromstring(html)
                html_.rewrite_links(self._rewrite_link(resources))
                html = tostring(html_)

                if save_as_markdown:
                    content = converter.html_to_markdown(html)

                manager.save_note(path, content)
                manager.clean_note_resources(path)

                return jsonify({
                    'path': path
                })
            return 200

        @self.socketio.on('connect')
        def on_connect():
            """
            This seems necessary to get
            the SocketIO emitting working properly...
            """
            logger.debug('User connected.')
