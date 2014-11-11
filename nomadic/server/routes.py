import os
import urllib
import mimetypes
from datetime import datetime

from flask import Blueprint, Response, render_template, request, jsonify, current_app

from nomadic import nomadic, conf
from nomadic.core.models import Note, Notebook, Path
from nomadic.util import html2md, md2html, parsers


routes = Blueprint('routes', __name__)

def quote(path):
    return urllib.quote(path.encode('utf-8'))


@routes.route('/override.css')
def stylesheet():
    """
    A stylesheet the user can specify in their config
    which will be loaded after the default one.
    """
    stylesheet = ''
    if conf.OVERRIDE_STYLESHEET:
        try:
            with open(conf.OVERRIDE_STYLESHEET, 'r') as f:
                stylesheet = f.read()
        except:
            current_app.logger.error('Specified override stylesheet was not found.')
    return Response(stylesheet, mimetype='text/css')


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

    if os.path.isdir(p.abs) or os.path.splitext(p.abs)[1] == '.md' or path == 'recent/':
        return render_template('index.html', tree=nomadic.rootbook.tree)

    elif os.path.isfile(p.abs):
        with open(p.abs, 'rb') as file:
            type, enc = mimetypes.guess_type(p.abs)
            return Response(file.read(), mimetype=type)

    else:
        return 'Not found.', 404


@routes.route('/nb/')
@routes.route('/nb/<path:path>')
def nb(path=''):
    """
    Returns JSON objects representing a Note or a Notebook,
    depending on the specified path.
    """

    # The `recent` path is a special case.
    if path == 'recent':
        name = 'most recently modified'
        sorted_notes = nomadic.rootbook.recent_notes[:20]
        url = 'recent'

    else:
        path = urllib.unquote(path)
        notebook = Notebook(path)
        name = notebook.name
        url = quote(notebook.path.rel)

        if os.path.isdir(notebook.path.abs):
            notebooks, notes = notebook.contents
            sorted_notes = sorted(notes, key=lambda x: x.last_modified, reverse=True)

    if sorted_notes:
        return jsonify({
            'name': name,
            'url': url,
            'notes': [{
                    'title': note.title,
                    'images': note.images,
                    'excerpt': note.excerpt,
                    'url': quote(note.path.rel)
                } for note in sorted_notes]
        })

    else:
        return 'Not found.', 404


@routes.route('/n/<path:path>', methods=['GET', 'PUT'])
def n(path):
    path = urllib.unquote(path)
    note = Note(path)

    if os.path.isfile(note.path.abs):

        if request.method == 'PUT':
            text = request.form['text']
            note.write(text)

        raw = note.content

        if note.ext == '.md':
            content = md2html.compile_markdown(raw)
        else:
            content = raw

        return jsonify({
            'title': note.title,
            'html': content,
            'path': path,
            'raw': raw,
            'nburl': quote(note.notebook.path.rel)
        })


    else:
        return 'Not found.', 404


@routes.route('/search', methods=['POST'])
def search():
    q = request.form['query']
    results = nomadic.index.search(q, html=True)

    return jsonify({
        'name': 'search results',
        'url': None,
        'notes': [{
                'title': note.title,
                'images': [os.path.join(note.notebook.path.rel, image) for image in note.images],
                'excerpt': highlights,
                'url': quote(note.path.rel)
            } for note, highlights in results]
    })


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
    form = request.form
    ext = '.md' if form['save_as_markdown'] else '.html'
    path = os.path.join(form['notebook'], form['title'] + ext)
    note = Note(path)

    if request.method == 'POST':
        save(note, form)
        return 'Created', 201

    elif request.method == 'PUT':
        save(note, form)
        return 'Updated', 200

    elif request.method == 'DELETE':
        note.delete()
        return 'Deleted', 204


def save(note, data):
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
                return 'Note already exists', 409

        html = parsers.rewrite_external_images(html, note)

        if note.ext == '.md':
            content = html2md.html_to_markdown(html)

        note.write(content)
        note.clean_resources()

        # Update all connected clients.
        #self.refresh_clients()

        return jsonify({
            'path': note.path.abs
        })
    return 'Success', 200


