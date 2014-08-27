"""
Server
=======================

Handles the web interface and
refreshing of connected clients.
"""

from flask import Flask, render_template, request, jsonify
from flask.ext.socketio import SocketIO

from nomadic.util import html2md, parsers
from nomadic.core.path import Path
from nomadic.core.models import Note
from nomadic.core.errors import NoteConflictError
from nomadic.demon.logger import log

import os
import shutil
import urllib
from datetime import datetime
import sys, logging

class Server():
    def __init__(self, nomadic, port):
        self.n = nomadic
        self.port = port

        self.app = Flask(__name__,
                static_folder='../assets/static',
                static_url_path='/static',
                template_folder='../assets/templates')

        self.socketio = SocketIO(self.app)
        self._build_routes()

        # Log to stdout.
        sh = logging.StreamHandler(sys.stdout)
        self.app.logger.addHandler(sh)

    def start(self):
        log.debug('starting the nomadic server...')
        self.socketio.run(self.app, port=self.port)

    def refresh_clients(self):
        self.socketio.emit('refresh')

    def _build_routes(self):
        @self.app.route('/<path:path>')
        def note(path):
            _, ext = os.path.splitext(path)
            p = Path(urllib.unquote(path))

            # Convert to build path if appropriate.
            if ext in ['.md', '.html']:
                path = self.n.builder.to_build_path(p.abs)
            else:
                path = p.abs

            try:
                with open(path, 'r') as file:
                    content = file.read()
            except IOError:
                return 'IOError', 404

            return content

        @self.app.route('/search', methods=['POST'])
        def search():
            q = request.form['query']
            results = self.n.index.search(q, html=True)
            return render_template('results.html', results=results)

        @self.app.route('/new')
        def new():
            # A unique default title to save without conflicts.
            default_title = datetime.utcnow()
            return render_template('editor.html', notebooks=self.n.rootbook.notebooks, title=default_title)

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

    def _process_form(self, form):
        ext = '.md' if form['save_as_markdown'] else '.html'
        path = os.path.join(form['notebook'], form['title'] + ext) 
        return Note(path)

    def delete(self, form):
        note = self._process_form(form)
        note.delete()
        return 'Success', 200

    def save(self, form):
        html = form['html']

        if parsers.remove_html(html):
            note = self._process_form(form)
            path_new = os.path.join(form['new[notebook]'], form['new[title]'] + note.ext)

            # If the title or notebook has changed,
            # move the note by updating its path.
            if note.path.abs != path_new:
                try:
                    note.move(path_new)
                except NoteConflictError:
                    # 409 = Conflict
                    self.app.log.debug('Note at {0} already exists.'.format(path_new))
                    return 'Note already exists', 409

            html = parsers.rewrite_external_images(html, note)

            if note.ext == '.md':
                content = html2md.html_to_markdown(html)

            note.write(content)
            note.clean_resources()

            # Update all connected clients.
            self.refresh_clients()

            return jsonify({
                'path': note.path.abs
            })
        return 'Success', 200


