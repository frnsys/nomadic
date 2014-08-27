import os
from urllib import quote

from nomadic.core import Notebook, Note, Builder
from test import NomadicTest, _path, compiled_path

class BuildTest(NomadicTest):
    def setUp(self):
        self.builder = Builder(self.notes_dir)

    def test_build_notes(self):
        self.builder.build()

        for build_path in ['index.html', 'my note.html', 'some_notebook/index.html', 'some_notebook/a cool note.html']:
            path = compiled_path(build_path)
            self.assertTrue(os.path.exists(path))

    def test_compile_note(self):
        note = Note(_path('my note.md'))
        self.builder.compile_note(note)

        path = compiled_path('my note.html')
        self.assertTrue(os.path.exists(path))

    def test_compiled_note_relative_urls_become_absolute(self):
        self.builder.build()

        path = _path('some_notebook/a cool note.md')
        with open(path, 'r') as note:
            self.assertTrue('a cool note.resources/some_image.png' in note.read())

        path_ = compiled_path('some_notebook/a cool note.html')
        with open(path_, 'r') as note:
            expected = '../../some_notebook/a cool note.resources/some_image.png'
            self.assertTrue(quote(expected) in note.read())

    def test_compiled_note_markdown_urls_become_html(self):
        self.builder.build()

        path = _path('some_notebook/a cool note.md')
        with open(path, 'r') as note:
            self.assertTrue('nested book/empty.md' in note.read())

        path_ = compiled_path('some_notebook/a cool note.html')
        with open(path_, 'r') as note:
            self.assertTrue(quote('nested book/empty.html') in note.read())

    def test_compile_note_overwrites(self):
        note = Note(_path('my note.md'))
        self.builder.compile_note(note)

        path_ = compiled_path('my note.html')
        with open(path_, 'r') as n:
            self.assertTrue('<h1 id="hey-hi">HEY HI</h1>\n<p>foo bar qua</p>' in n.read())

        note.write(u'changed note content')

        self.builder.compile_note(note)

        with open(path_, 'r') as n:
            note_content = n.read()
            self.assertTrue('<p>changed note content</p>' in note_content)
            self.assertFalse('<h1>HEY HI</h1>\n<p>foo bar qua</p>' in note_content)

    def test_delete_compiled_note(self):
        note = Note(_path('my note.md'))
        path_ = compiled_path('my note.html')

        self.builder.compile_note(note)
        self.assertTrue(os.path.exists(path_))

        self.builder.delete_note(note)
        self.assertFalse(os.path.exists(path_))

    def test_compiled_index(self):
        self.builder.build()

        path = compiled_path('some_notebook/index.html')
        with open(path, 'r') as ix:
            self.assertTrue(quote('a cool note.html') in ix.read())

    def test_update_compiled_index(self):
        self.builder.build()

        path = compiled_path('some_notebook/index.html')
        with open(path, 'r') as ix:
            self.assertTrue(quote('a new note.html') not in ix.read())

        new_note = Note(_path('some_notebook/a new note.md'))
        new_note.write(u'new note')
        self.builder.compile_note(new_note)

        notebook = Notebook(_path('some_notebook'))
        self.builder.index_notebook(notebook)

        with open(path, 'r') as ix:
            self.assertTrue(quote('a new note.html') in ix.read())

    def test_delete_notebook(self):
        self.builder.build()

        path = compiled_path('some_notebook')
        self.assertTrue(os.path.exists(path))

        notebook = Notebook(_path('some_notebook'))
        self.builder.delete_notebook(notebook)

        self.assertFalse(os.path.exists(path))
