import os
from urllib import parse
from datetime import datetime
from nomadic import nomadic, conf
from nomadic.core.errors import NoteConflictError
from nomadic.core.models import Note, Notebook, Path
from nomadic.util import html2md, md2html, parsers
from flask import Blueprint, Response, render_template, request, jsonify, current_app, url_for, send_file


routes = Blueprint('routes', __name__)


def breadcrumbs(path):
    """generates breadcrumbs for a given path"""
    breadcrumbs = []
    url = '/'
    for part in path.strip('/').split('/'):
        if part.endswith('.md'):
            url += part
        else:
            url += part + '/'
        breadcrumbs.append((url_for('routes.handle', path=url), part))
    return breadcrumbs


@routes.route('/override.css')
def stylesheet():
    """a stylesheet the user can specify in their config
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
    - if the path looks like a note, serve the note
    - if the path looks like a notebook, server the notebook
    - otherwise, serves the file content.
    """
    p = Path(parse.unquote(path))

    if os.path.isdir(p.abs) or path == 'recent/':
        return view_notebook(path)

    elif os.path.splitext(p.abs)[1] == '.md':
        return view_note(path)

    elif os.path.isfile(p.abs):
        # with open(p.abs, 'rb') as file:
            # return send_file(p.abs)
        return send_file(open(p.abs, ('rb')))

    else:
        return 'Not found.', 404


@routes.route('/notebooks')
def view_notebooks():
    recent = Notebook('recent')
    return render_template('notebooks.html', tree=[recent] + nomadic.rootbook.tree)


def view_notebook(path):
    """returns a notebook at the specified path"""
    # The `recent` path is a special case.
    if path == 'recent/':
        name = 'most recently modified'
        sorted_notes = nomadic.rootbook.recent_notes[:20]

    else:
        path = parse.unquote(path)
        notebook = Notebook(path)
        name = notebook.name

        if os.path.isdir(notebook.path.abs):
            notebooks, notes = notebook.contents
            sorted_notes = sorted(notes, key=lambda x: x.last_modified, reverse=True)
        else:
            return 'Not found.', 404

    return render_template('notebook.html',
        notebook={
            'name': name,
            'notes': [{
                'title': note.title,
                'images': [os.path.join('/', note.notebook.path.rel, image) for image in note.images],
                'excerpt': note.excerpt,
                'url': parse.quote(note.path.rel)
            } for note in sorted_notes],
        }, breadcrumbs=breadcrumbs(path))


def view_note(path):
    path = parse.unquote(path)
    note = Note(path)

    if os.path.isfile(note.path.abs):
        if note.ext == '.md':
            content = md2html.compile_markdown(note.content)
        else:
            content = note.content

        return render_template('note.html',
            note={
                'title': note.title,
                'html': content,
                'path': path,
            }, breadcrumbs=breadcrumbs(path))
    else:
        return 'Not found.', 404


@routes.route('/search')
def search():
    q = request.args.get('query', None)


    if q is not None:
        name = 'search results'
        if '--include_pdf' in q:
            q = q.replace('--include_pdf', '')
            include_pdf = True
        else:
            include_pdf = False
        results = nomadic.search(q,
                                 delimiters=('<b class="match">', '</b>'),
                                 include_pdf=include_pdf)
    else:
        name = 'search'
        results = []

    return render_template('notebook.html',
        notebook={
            'name': name,
            'notes': [{
                'title': note.title,
                'images': [os.path.join('/', note.notebook.path.rel, image) for image in note.images],
                'excerpt': '<br>'.join(highlights),
                'url': parse.quote(note.path.rel)
            } for note, highlights in results]
        }, breadcrumbs=[])


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


