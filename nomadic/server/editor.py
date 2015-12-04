import os
from datetime import datetime
from nomadic import nomadic, conf
from nomadic.core.models import Note
from nomadic.util import html2md, parsers
from nomadic.core.errors import NoteConflictError
from flask import Blueprint, render_template, request, jsonify


routes = Blueprint('editor', __name__)


@routes.route('/new')
def new():
    # a unique default title to save without conflicts.
    default_title = datetime.utcnow()
    return render_template('editor.html', notebooks=nomadic.rootbook.notebooks, title=default_title)


@routes.route('/upload', methods=['POST'])
def upload():
    """for uploading images from the editor"""
    file = request.files['file']
    allowed_content_types = ['image/gif', 'image/jpeg', 'image/png']
    content_type = file.headers['Content-Type']

    if content_type in allowed_content_types:
        path = os.path.join(request.form['notebook'], request.form['title'] + '.ext') # some arbitrary extension
        note = Note(path)

        assets = note.assets
        if not os.path.exists(assets):
            os.makedirs(assets)

        # Build a unique filename.
        _, ext = os.path.splitext(file.filename)
        if not ext:
            ext = '.' + content_type.split('/')[-1]
        if ext == '.jpeg': ext = '.jpg'
        filename = str(hash(file.filename + str(datetime.utcnow()))) + ext

        save_path = os.path.join(assets, filename)

        file.save(save_path)
        return save_path.replace(conf.ROOT, ''), 200

    else:
        return 'Content type of {0} not allowed'.format(content_type), 415


@routes.route('/note', methods=['POST', 'PUT', 'DELETE'])
def editor():
    """endpoints for the editor"""
    form = request.form
    ext = '.md'
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
    """for use with the editor"""
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
        note.clean_assets()

        return jsonify({
            'path': note.path.abs
        })
    return 'Success', 200


