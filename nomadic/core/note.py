import os
import shutil

from nomadic.core.path import Path
from nomadic.util import pdf, parsers


class NoteConflictError(Exception):
    pass


class Note():
    def __init__(self, path):
        self.path = Path(path)

        _, filename = os.path.split(path)
        self.title, self.ext = os.path.splitext(filename)


    @property
    def content(self):
        if self.ext == '.pdf':
            return pdf.pdf_text(self.path.abs)

        with open(self.path.abs, 'rb') as note:
            return note.read().decode('utf-8')


    @property
    def plaintext(self):
        text = u''
        if self.ext == '.pdf':
            text = self.content

        else:
            if self.ext == '.html':
                text = parsers.remove_html(self.content)
            elif self.ext == '.md':
                text = parsers.remove_md(self.content)

        if type(text) is str:
            text = text.decode('utf-8')

        return text

    @property
    def excerpt(self):
        char_limit = 400
        excerpt = self.plaintext
        if len(excerpt) > char_limit:
            excerpt = excerpt[:char_limit-3] + '...'
        return excerpt

    @property
    def last_modified(self):
        return os.path.getmtime(self.path.abs)


    @property
    def resources(self, create=False):
        notebook, filename = os.path.split(self.path.abs)
        resources = os.path.join(notebook, '_resources', self.title, '')

        if create and not os.path.exists(resources):
            os.makedirs(resources)

        return resources


    def write(self, content):
        with open(self.path.abs, 'w') as note:
            note.write(content.encode('utf-8'))


    def move(self, dest):
        to_note = Note(dest)

        if os.path.exists(to_note.path.abs):
            raise NoteConflictError()

        if os.path.exists(self.path.abs):
            shutil.move(self.path.abs, to_note.path.abs)

        if os.path.exists(self.resources):
            shutil.move(self.resources, to_note.resources)

        self.path = to_note.path
        self.title = to_note.title
        self.ext = to_note.ext


    def delete(self):
        if os.path.exists(self.path.abs):
            os.remove(self.path.abs)

        resources = self.resources
        if os.path.exists(resources):
            shutil.rmtree(resources)


    def clean_resources(self):
        """
        Delete resources which are not
        referenced by the note.
        """
        r = self.resources
        if os.path.exists(r):
            content = self.content
            for name in os.listdir(r):
                p = os.path.join(r, name)
                if os.path.isfile(p) and name not in content:
                    os.remove(p)
