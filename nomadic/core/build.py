"""
Build
=======================

Build note files a local HTML site
and manage built files.
"""

import os
import shutil

from jinja2 import Template, FileSystemLoader, environment

from nomadic.core import Notebook, Note
from nomadic.util import md2html, parsers

# Load templates.
path = os.path.abspath(__file__)
dir = os.path.dirname(path)

env = environment.Environment()
env.loader = FileSystemLoader(os.path.join(dir, '../assets/templates'))
notebook_templ = env.get_template('notebook.html')
note_templ = env.get_template('note.html')

class Builder():
    def __init__(self, notes_path):
        # The last '' is to ensure a trailing slash.
        self.notes_path = os.path.join(notes_path, '')
        self.build_path = os.path.join(notes_path, u'.build', '')
        self._prepare_build_dir()


    def _prepare_build_dir(self, reset=False):
        if reset and os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)

        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)


    def build(self):
        rootbook = Notebook(self.notes_path)
        self._prepare_build_dir(reset=True)
        self.compile_notebook(rootbook)


    def compile_notebook(self, notebook):
        """
        Build a notebook, recursively, compiling notes and indexes.
        """
        for root, notebooks, notes in notebook.walk():
            build_root = root.replace(self.notes_path, self.build_path)

            for notebook in notebooks:
                build_path = os.path.join(build_root, notebook.name)

                if os.path.exists(build_path):
                    shutil.rmtree(build_path)
                os.makedirs(build_path)

            for note in notes:
                self.compile_note(note)

            # Write the index file for this node.
            self._write_index(build_root, notebooks, notes)


    def compile_note(self, note):
        """
        Compile a single Markdown or HTML note to the build tree.
        This will overwrite the existing note, if any.
        """

        build_path = self.to_build_path(note.path.abs)
        crumbs = self._build_breadcrumbs(build_path)
        raw = note.content

        if note.ext != '.html':
            raw = md2html.compile_markdown(raw)

        if raw.strip():
            # Process all relative paths to point to the raw note directories,
            # so we don't have to copy resources over.
            raw = parsers.rewrite_links(raw, self._rewrite_link(note.path.abs, build_path))

        content = note_templ.render(note=note, html=raw, crumbs=crumbs)

        # Write the compiled note.
        with open(build_path, 'w') as build_note:
            build_note.write(content.encode('utf-8'))


    def delete_note(self, note):
        build_path = self.to_build_path(note.path.abs)
        if os.path.exists(build_path):
            os.remove(build_path)


    def delete_notebook(self, notebook):
        build_path = self.to_build_path(notebook.path.abs)
        if os.path.exists(build_path):
            shutil.rmtree(build_path)


    def index_notebook(self, notebook):
        """
        Compiles an index for a given directory.
        This does not compile the notes in the directory,
        nor is it recursive.
        """
        build_path = self.to_build_path(notebook.path.abs)
        notebooks, notes = notebook.contents
        self._write_index(build_path, notebooks, notes)


    def to_build_path(self, path):
        if '.build' not in path:
            if path.endswith('.md'):
                base, _ = os.path.splitext(path)
                path = base + '.html'

            path = os.path.normpath(path)
            if os.path.isdir(path):
                path = os.path.join(path, '')
            path = path.replace(self.notes_path, self.build_path)
        return path


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


    def _build_breadcrumbs(self, path):
        # Get rid of the build path.
        path = path.replace(self.build_path, '')

        # Create some name for the root notebook.
        path = os.path.join('notes', path)

        # Split the path into the crumbs.
        # Filter out any empty crumbs.
        crumbs = filter(None, path.split('/'))

        # Remove the file extension from the last crumb.
        crumbs[-1], _ = os.path.splitext(crumbs[-1])

        return crumbs


    def _rewrite_link(self, path, build_path):
        # Build the relative base path for the note's references.
        note_dir = os.path.split(path.replace(self.notes_path, ''))[0]
        note_build_dir = build_path.replace(self.notes_path, '')
        depth = len(note_build_dir.split('/')) - 1
        base_path = os.path.join(('../' * depth), note_dir, '')

        def rewriter(link):
            # Ignore external, absolute, and hash links.
            if not link.startswith(('http', '/', '#')):
                root, ext = os.path.splitext(link)

                # Update references to non-note files
                # so that they point outside the build directory.
                if ext not in ['.html', '.md']:
                    return os.path.join(base_path, link)

                elif ext == '.md':
                    return root + '.html'
            return link
        return rewriter
