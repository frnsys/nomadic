import os
import shutil
import operator
from urllib.parse import quote
from nomadic import conf
from nomadic.core.errors import NoteConflictError
from nomadic.util import parsers, valid_notebook, valid_note


class Path():
    def __init__(self, path):
        if os.path.isabs(path):
            self.abs = path
            self.rel = os.path.relpath(path, conf.ROOT)
        else:
            self.rel = path
            self.abs = os.path.join(conf.ROOT, path)


class Note():
    def __init__(self, path):
        self.path = Path(path)

        _, self.filename = os.path.split(self.path.rel)
        self.title, self.ext = os.path.splitext(self.filename)

        # only assume absolute path if the path is relative
        if not os.path.isabs(path):
            notebook_path = os.path.dirname(self.path.rel)
        else:
            notebook_path = os.path.dirname(path)
        self.notebook = Notebook(notebook_path)

    @property
    def plaintext(self):
        if self.ext == '.pdf':
            return self.content

        elif self.ext == '.md':
            return parsers.remove_md(self.content)

    @property
    def content(self):
        if self.ext == '.pdf':
            return '[PDF]'

        with open(self.path.abs, 'r') as note:
            return note.read()

    @property
    def excerpt(self, char_limit=200):
        """a plaintext excerpt of the note's contents"""
        excerpt = self.plaintext
        if len(excerpt) > char_limit:
            excerpt = excerpt[:char_limit-3] + '...'
        return excerpt

    @property
    def images(self):
        """paths to images referenced in this note"""
        if self.ext == '.md':
            return parsers.md_images(self.content)
        return []

    @property
    def last_modified(self):
        return os.path.getmtime(self.path.abs)

    @property
    def assets(self, create=False):
        """path to the note's assets"""
        notebook, filename = os.path.split(self.path.abs)
        assets = os.path.join(notebook, 'assets', self.title, '')

        if create and not os.path.exists(assets):
            os.makedirs(assets)

        return assets

    def write(self, content):
        with open(self.path.abs, 'w') as note:
            note.write(content)

    def move(self, dest):
        """move the note and its assets"""
        to_note = Note(dest)

        if os.path.exists(to_note.path.abs):
            raise NoteConflictError()

        if os.path.exists(self.path.abs):
            shutil.move(self.path.abs, to_note.path.abs)

        if os.path.exists(self.assets):
            shutil.move(self.assets, to_note.assets)

        self.path = to_note.path
        self.title = to_note.title
        self.ext = to_note.ext

    def delete(self):
        """deletes the note and its assets"""
        if os.path.exists(self.path.abs):
            os.remove(self.path.abs)

        assets = self.assets
        if os.path.exists(assets):
            shutil.rmtree(assets)

    def clean_assets(self, delete=False):
        """delete assets which are not referenced by the note.
        only actually deletes if `delete=True`"""
        action = 'Deleting' if delete else 'Will delete'
        r = self.assets
        if os.path.exists(r):
            content = self.content
            for name in os.listdir(r):
                p = os.path.join(r, name)
                if os.path.isfile(p) \
                    and (name not in content and quote(name) not in content):
                    print('{0} {1} for {2}'.format(action, name, self.title))
                    if delete:
                        os.remove(p)

            # Remove the entire directory if empty.
            if not os.listdir(r):
                print('{0} assets folder for {1}'.format(action, self.title))
                if delete:
                    shutil.rmtree(r)


class Notebook():
    def __init__(self, path):
        self.path = Path(path)
        self.name = os.path.basename(path)

    @property
    def notebooks(self):
        """sub-notebooks of this notebook"""
        for root, notebooks, notes in self.walk():
            yield from notebooks

    @property
    def notes(self):
        """all notes, recursively, for this notebook"""
        for root, notebooks, notes in self.walk():
            yield from notes

    @property
    def recent_notes(self):
        """all notes in this notebook, recursively,
        sorted by last modified (most recent first)"""
        return sorted(
                [n for n in self.notes],
                key=operator.attrgetter('last_modified'),
                reverse=True)

    @property
    def tree(self):
        """get tree structure of this notebook's sub-notebooks

        E.g::

            [
                notebook,
                notebook
                [
                    notebook,
                    notebook
                ],
                notebook
            ]
        """
        tree = []

        notebooks, _ = self.contents
        for nb in notebooks:
            tree.append(nb)
            subtree = nb.tree
            if subtree:
                tree.append(subtree)
        return tree

    @property
    def contents(self):
        """names of all files and directories
        in this notebook, _not_ recursively"""
        notebooks, notes = [], []
        for name in os.listdir(self.path.abs):
            p = os.path.join(self.path.abs, name)
            if os.path.isfile(p) and valid_note(p):
                notes.append(Note(p))
            else:
                if valid_notebook(p):
                    notebooks.append(Notebook(p))
        return notebooks, notes

    def clean_assets(self, delete=False):
        """clean up individual notes' assets,
        and delete assets which no longer have parent notes.
        only actually deletes if `delete=True`"""
        action = 'Deleting' if delete else 'Will delete'
        r = os.path.join(self.path.abs, 'assets')
        _, notes = self.contents

        # Delete orphaned assets.
        note_titles = [note.title for note in notes]
        if os.path.exists(r):
            for name in os.listdir(r):
                if name not in note_titles:
                    p = os.path.join(r, name)
                    print('{0} asset folder: {1}'.format(action, name))
                    if delete:
                        shutil.rmtree(p)

        # Delete unreferenced assets.
        for note in notes:
            note.clean_assets(delete=delete)

    def walk(self):
        """walks the notebook, yielding only
        valid directories and files."""
        for root, dirs, files in os.walk(self.path.abs):
            if valid_notebook(root):
                notebooks, notes = [], []
                for dir in dirs:
                    path = os.path.join(root, dir)
                    if valid_notebook(path):
                        notebooks.append(Notebook(path))
                for file in files:
                    if valid_note(file):
                        path = os.path.join(root, file)
                        notes.append(Note(path))

                yield root, notebooks, notes
