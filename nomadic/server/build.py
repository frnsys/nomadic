"""
Build
=======================

Build note files a local HTML site
and manage built files.
"""

import os
import shutil

from nomadic.core import Notebook, Note
from nomadic.util import md2html

def compile_note(self, note):
    """
    Compile a single Markdown or HTML note to the build tree.
    This will overwrite the existing note, if any.
    """

    build_path = self.to_build_path(note.path.abs)
    crumbs = self._build_breadcrumbs(build_path)
    raw = note.content

    if note.ext == '.pdf':
        return

    if note.ext != '.html':
        raw = md2html.compile_markdown(raw)

    content = note_templ.render(note=note, html=raw, crumbs=crumbs)

    # Write the compiled note.
    with open(build_path, 'w') as build_note:
        build_note.write(content.encode('utf-8'))


def index_notebook(self, notebook):
    """
    Compiles an index for a given directory.
    This does not compile the notes in the directory,
    nor is it recursive.
    """
    build_path = self.to_build_path(notebook.path.abs)
    notebooks, notes = notebook.contents
    self._write_index(build_path, notebooks, notes)


def _write_index(self, path, notebooks, notes):
    """
    Write an `index.html` file at the specified path,
    listing the specified dirs and files.
    """
    crumbs = self._build_breadcrumbs(path)

    # Most recent come first.
    sorted_notes = sorted(notes, key=lambda x: x.last_modified, reverse=True)
    rendered = notebook_templ.render(notebooks=notebooks, notes=sorted_notes, crumbs=crumbs)

    if not os.path.exists(path):
        os.makedirs(path)

    with open( os.path.join(path, 'index.html'), 'w' ) as index:
        index.write(rendered.encode('utf-8'))
