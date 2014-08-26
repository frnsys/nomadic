import shutil
from os.path import exists

from nomadic.core import Note
from test import NomadicTest, _path


class NoteTest(NomadicTest):
    def test_initialization(self):
        note = Note('/foo/bar/my note.md')

        self.assertEquals(note.title, 'my note')
        self.assertEquals(note.ext, '.md')
        self.assertEquals(note.path.abs, '/foo/bar/my note.md')

    def test_get_note_resources_path(self):
        note = Note('/foo/bar/my note.md')
        self.assertEqual(note.resources, '/foo/bar/_resources/my note/')

    def test_delete_note(self):
        src = _path('my note.md')
        src_resource = _path('_resources/my note/foo.jpg')

        self.assertTrue(exists(src))
        self.assertTrue(exists(src_resource))

        note = Note(src)
        note.delete()

        self.assertFalse(exists(src))
        self.assertFalse(exists(src_resource))

    def test_move_note(self):
        src = _path('my note.md')
        dest = _path('some_notebook/my moved note.md')

        src_resource = _path('_resources/my note/foo.jpg')
        dest_resource = _path('some_notebook/_resources/my moved note/foo.jpg')

        note = Note(src)
        note.move(dest)

        self.assertTrue(exists(dest))
        self.assertTrue(exists(dest_resource))

        self.assertFalse(exists(src))
        self.assertFalse(exists(src_resource))

        self.assertEquals(note.path.abs, dest)
        self.assertEquals(note.title, 'my moved note')

    def test_clean_note_resources(self):
        note = Note(_path('my note.md'))
        note_resource = _path('_resources/my note/foo.jpg')

        self.assertTrue(exists(note_resource))

        note.clean_resources()

        self.assertFalse(exists(note_resource))

    def test_content_pdf(self):
        note = Note(_path('womp.pdf'))
        self.assertEqual(note.content, 'I\'m a PDF')

    def test_plaintext_markdown(self):
        note = Note(_path('my note.md'))
        self.assertEqual(note.plaintext, 'HEY HI\nfoo bar qua')

    def test_plaintext_html(self):
        note = Note(_path('test.html'))
        self.assertEqual(note.plaintext, 'Test HTML\n\n\n\n\n    This is a test')
