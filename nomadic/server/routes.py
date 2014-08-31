import os
import urllib
import mimetypes
from datetime import datetime

from flask import Blueprint, Response, render_template, request, jsonify

from nomadic import nomadic
from nomadic.core.path import Path
from nomadic.core import Note, Notebook
from nomadic.server import build
from nomadic.util import html2md, md2html, parsers


routes = Blueprint('routes', __name__)


@routes.route('/')
@routes.route('/<path:path>')
def handle(path=''):
    """
    Primary route.
    - If the path looks like a Note or a Notebook, serves the index page
    to let Backbone do the routing.
    - Otherwise, serves the file content.
    """
    p = Path(urllib.unquote(path))

    if os.path.isdir(p.abs) or os.path.splitext(p.abs)[1] == '.md':
        return render_template('index.html')

    elif os.path.isfile(p.abs):
        with open(p.abs, 'rb') as file:
            type, enc = mimetypes.guess_type(p.abs)
            return Response(file.read(), mimetype=type)

    else:
        return 'Not found.', 404


@routes.route('/n/')
@routes.route('/n/<path:path>')
def n(path=''):
    """
    Returns JSON objects representing a Note or a Notebook,
    depending on the specified path.
    """
    p = Path(urllib.unquote(path))

    # Notebook
    if os.path.isdir(p.abs):
        notebook = Notebook(p.abs)
        notebooks, notes = notebook.contents

        return jsonify({
            'type': 'notebook',
            'name': notebook.name,
            'notes': [{
                    'title': note.title,
                    'images': [os.path.join(notebook.name, image) for image in note.images],
                    'excerpt': note.excerpt,
                    'url': note.path.rel
                } for note in notes],
            'notebooks': [{
                    'name': notebook.name,
                    'url': notebook.path.rel
                } for notebook in notebooks]
        })

    # Note
    elif os.path.isfile(p.abs):
        note = Note(p.abs)
        content = note.content

        if note.ext == '.md':
            content = md2html.compile_markdown(content)

        return jsonify({
            'type': 'note',
            'title': note.title,
            'html': content
        })

    else:
        return 'Not found.', 404


@routes.route('/search', methods=['POST'])
def search():
    q = request.form['query']
    results = nomadic.index.search(q, html=True)
    return render_template('results.html', results=results)


@routes.route('/new')
def new():
    # A unique default title to save without conflicts.
    default_title = datetime.utcnow()
    return render_template('editor.html', notebooks=nomadic.rootbook.notebooks, title=default_title)


@routes.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    allowed_content_types = ['image/gif', 'image/jpeg', 'image/png']
    content_type = file.headers['Content-Type']
    if content_type in allowed_content_types:
        path = os.path.join(request.form['notebook'], request.form['title'] + '.ext') # some arbitrary extension
        note = Note(path)

        resources = note.resources
        if not os.path.exists(resources):
            os.makedirs(resources)

        # Build a unique filename.
        _, ext = os.path.splitext(file.filename)
        if not ext:
            ext = '.' + content_type.split('/')[-1]
        if ext == '.jpeg': ext = '.jpg'
        filename = str(hash(file.filename + str(datetime.utcnow()))) + ext

        save_path = os.path.join(resources, filename)

        file.save(save_path)
        return save_path.replace(server.n.notes_path, ''), 200

    else:
        return 'Content type of {0} not allowed'.format(content_type), 415


@routes.route('/note', methods=['POST', 'PUT', 'DELETE'])
def editor():
    ext = '.md' if form['save_as_markdown'] else '.html'
    path = os.path.join(form['notebook'], form['title'] + ext) 
    note = Note(path)

    if request.method == 'POST':
        save(note, request.form)
        return 'Created', 201

    elif request.method == 'PUT':
        save(note, request.form)
        return 'Updated', 200

    elif request.method == 'DELETE':
        note.delete()
        return 'Deleted', 204


def save(self, note, data):
    html = data['html']

    if parsers.remove_html(html):
        path_new = os.path.join(data['new[notebook]'], data['new[title]'] + note.ext)

        # If the title or notebook has changed,
        # move the note by updating its path.
        if note.path.abs != path_new:
            try:
                note.move(path_new)
            except NoteConflictError:
                # 409 = Conflict
                self.app.logger.debug('Note at {0} already exists.'.format(path_new))
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


