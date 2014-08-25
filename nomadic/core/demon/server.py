from flask import Flask, render_template, request, jsonify
from flask.ext.socketio import SocketIO

from nomadic.core import manager
from nomadic.core.builder import converter
from nomadic.core.demon.logger import log

import os
import shutil
import urllib
from datetime import datetime
import sys, logging

from lxml.html import fromstring, tostring

class Server():
    def __init__(self, nomadic, port):
        self.n = nomadic
        self.port = port

        self.app = Flask(__name__,
                static_folder='../assets/static',
                static_url_path='/static',
                template_folder='../assets/templates')

        self.socketio = SocketIO(self.app)
        self.build_routes()

        # To log errors to stdout.
        # Can't really use Flask's debug w/ the websocket lib,
        # but this accomplishes the same thing.
        sh = logging.StreamHandler(sys.stdout)
        self.app.logger.addHandler(sh)

    def start(self):
        log.debug('Starting the nomadic server...')
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
                return save_path.replace(self.n.notes_path, '')
            return link
        return rewriter

    def build_routes(self):
        @self.app.route('/<path:note_path>')
        def note(note_path):
            note_path = os.path.join(self.n.notes_path, note_path)

            # Convert to build path if appropriate.
            if note_path.endswith(('.md', '.html')):
                note_path, _ = self.n.builder.build_path_for_note_path(note_path)

            with open(note_path, 'r') as note:
                content = note.read()
            return content

        @self.app.route('/search', methods=['POST'])
        def search():
            q = request.form['query']
            results = searcher.search(q, self.n.index, html=True)
            return render_template('results.html', results=results)

        @self.app.route('/new')
        def new():
            # A unique default title to save without conflicts.
            default_title = datetime.utcnow()
            return render_template('editor.html', notebooks=self.n.manager.notebooks, title=default_title)

        @self.app.route('/upload', methods=['POST'])
        def upload():
            file = request.files['file']

            allowed_content_types = ['image/gif', 'image/jpeg', 'image/png']
            content_type = file.headers['Content-Type']
            if content_type in allowed_content_types:
                title = request.form['title']
                notebook = request.form['notebook']
                path = os.path.join(notebook, title + '.ext') # some arbitrary extension

                # Build a unique filename.
                _, ext = os.path.splitext(file.filename)
                if not ext:
                    ext = '.' + content_type.split('/')[-1]
                if ext == '.jpeg': ext = '.jpg'
                filename = str(hash(file.filename + str(datetime.utcnow()))) + ext

                resources = self.n.manager.note_resources(path, create=True)
                save_path = os.path.join(resources, filename)

                file.save(save_path)
                return save_path.replace(self.n.notes_path, ''), 200

            else:
                return 'Content type of {0} not allowed'.format(content_type), 415

        @self.app.route('/note', methods=['POST', 'PUT', 'DELETE'])
        def editor():
            if request.method in ['POST', 'PUT']:
                return self.save(request.form)
            if request.method == 'DELETE':
                return self.delete(request.form)

        @self.socketio.on('connect')
        def on_connect():
            """
            This seems necessary to get
            the SocketIO emitting working properly...
            """
            log.debug('User connected.')

    def delete(self, data):
        title = data['title']
        notebook = data['notebook']

        for ext in ['.md', '.html']:
            path = os.path.join(notebook, title + ext)
            self.n.manager.delete_note(path)
        return 'Success', 200

    def save(self, data):
        html = data['html']

        if html:
            save_as_markdown = data['save_as_markdown']
            if save_as_markdown:
                ext = '.md'
            else:
                ext = '.html'

            title = data['title']
            notebook = data['notebook']
            path = os.path.join(notebook, title + ext) 

            title_new = data['new[title]']
            notebook_new = data['new[notebook]']
            path_new = os.path.join(notebook_new, title_new + ext)

            # If the title or notebook has changed,
            # move the note by updating its path.
            if path != path_new:

                # Check if the new path exists already.
                # We don't want to overwrite existing notes.
                if os.path.exists(path_new):
                    # 409 = Conflict
                    self.app.log.debug('Note at {0} already exists.'.format(path_new))
                    return 'Note already exists', 409

                self.n.manager.move_note(path, path_new)
                path = path_new

            resources = self.n.manager.note_resources(path)
            html_ = fromstring(html)
            html_.rewrite_links(self._rewrite_link(resources))
            html = tostring(html_)

            if save_as_markdown:
                content = converter.html_to_markdown(html)

            self.n.manager.save_note(path, content)
            self.n.manager.clean_note_resources(path)

            # Update all connected clients.
            self.refresh_clients()

            return jsonify({
                'path': path
            })
        return 'Success', 200


