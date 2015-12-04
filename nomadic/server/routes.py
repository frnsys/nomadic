import os
from urllib import parse
from nomadic import nomadic, conf
from nomadic.util import md2html
from nomadic.core.models import Note, Notebook, Path
from flask import Blueprint, Response, render_template, request, current_app, url_for, send_file


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
    which will be loaded after the default one."""
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
    """returns the notebook at the specified path"""
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
    """returns the note at the specified path"""
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
                                 include_pdf=include_pdf,
                                 html_out=True)
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
