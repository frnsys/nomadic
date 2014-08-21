import os
from urllib import quote

from nomadic.builder import Builder
from test import NomadicTest, note_at, compiled_path

class BuilderTest(NomadicTest):
    def setUp(self):
        self.builder = Builder(self.notes_dir)

    def test_build_notes(self):
        self.builder.build()

        for build_path in ['index.html', 'my note.html', 'some_notebook/index.html', 'some_notebook/a cool note.html']:
            path = compiled_path(build_path)
            self.assertTrue(os.path.exists(path))

    def test_compile_note(self):
        self.builder.compile_note(note_at('my note.md'))

        path = compiled_path('my note.html')
        self.assertTrue(os.path.exists(path))

    def test_compiled_note_relative_urls_become_absolute(self):
        self.builder.build()

        path = note_at('some_notebook/a cool note.md')
        with open(path, 'r') as note:
            self.assertTrue('a cool note.resources/some_image.png' in note.read())

        path_ = compiled_path('some_notebook/a cool note.html')
        with open(path_, 'r') as note:
            expected = '{0}/some_notebook/a cool note.resources/some_image.png'.format(self.notes_dir) 
            self.assertTrue(quote(expected) in note.read())

    def test_compiled_note_markdown_urls_become_html(self):
        self.builder.build()

        path = note_at('some_notebook/a cool note.md')
        with open(path, 'r') as note:
            self.assertTrue('nested book/empty.md' in note.read())

        path_ = compiled_path('some_notebook/a cool note.html')
        with open(path_, 'r') as note:
            self.assertTrue(quote('nested book/empty.html') in note.read())

    def test_compile_note_overwrites(self):
        path = note_at('my note.md')
        self.builder.compile_note(path)

        path_ = compiled_path('my note.html')
        with open(path_, 'r') as note:
            self.assertTrue('<h1>HEY HI</h1>\n<p>foo bar qua</p>' in note.read())

        with open(path, 'w') as note:
            note.write(u'changed note content')

        self.builder.compile_note(path)

        with open(path_, 'r') as note:
            note_content = note.read()
            self.assertTrue('<p>changed note content</p>' in note_content)
            self.assertFalse('<h1>HEY HI</h1>\n<p>foo bar qua</p>' in note_content)

    def test_delete_compiled_note(self):
        path = note_at('my note.md')
        path_ = compiled_path('my note.html')

        self.builder.compile_note(path)
        self.assertTrue(os.path.exists(path_))

        self.builder.delete_note(path)
        self.assertFalse(os.path.exists(path_))

    def test_compiled_index(self):
        self.builder.build()

        path = compiled_path('some_notebook/index.html')
        with open(path, 'r') as ix:
            self.assertTrue(u'a cool note.html' in ix.read())

    def test_update_compiled_index(self):
        self.builder.build()

        path = compiled_path('some_notebook/index.html')
        with open(path, 'r') as ix:
            self.assertTrue(u'a new note.html' not in ix.read())

        new_path = note_at('some_notebook/a new note.md')
        with open(new_path, 'w') as new_note:
            new_note.write(u'new note')
        self.builder.compile_note(new_path)

        self.builder.index_notebook(note_at('some_notebook'))

        with open(path, 'r') as ix:
            self.assertTrue(u'a new note.html' in ix.read())

    def test_delete_notebook(self):
        self.builder.build()

        path = compiled_path('some_notebook')
        self.assertTrue(os.path.exists(path))

        self.builder.delete_notebook(note_at('some_notebook'))

        self.assertFalse(os.path.exists(path))
