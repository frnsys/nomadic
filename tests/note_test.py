from os.path import exists

from nomadic.core import Note
from tests import NomadicTest, _path


class NoteTest(NomadicTest):
    def test_initialization(self):
        note = Note('/foo/bar/my note.md')

        self.assertEquals(note.title, 'my note')
        self.assertEquals(note.ext, '.md')
        self.assertEquals(note.path.abs, '/foo/bar/my note.md')

    def test_get_note_assets_path(self):
        note = Note('/foo/bar/my note.md')
        self.assertEqual(note.assets, '/foo/bar/assets/my note/')

    def test_delete_note(self):
        src = _path('my note.md')
        src_asset = _path('assets/my note/foo.jpg')

        self.assertTrue(exists(src))
        self.assertTrue(exists(src_asset))

        note = Note(src)
        note.delete()

        self.assertFalse(exists(src))
        self.assertFalse(exists(src_asset))

    def test_move_note(self):
        src = _path('my note.md')
        dest = _path('some_notebook/my moved note.md')

        src_asset = _path('assets/my note/foo.jpg')
        dest_asset = _path('some_notebook/assets/my moved note/foo.jpg')

        note = Note(src)
        note.move(dest)

        self.assertTrue(exists(dest))
        self.assertTrue(exists(dest_asset))

        self.assertFalse(exists(src))
        self.assertFalse(exists(src_asset))

        self.assertEquals(note.path.abs, dest)
        self.assertEquals(note.title, 'my moved note')

    def test_clean_note_assets(self):
        note = Note(_path('my note.md'))
        note_asset = _path('assets/my note/foo.jpg')

        self.assertTrue(exists(note_asset))
        note.clean_assets(delete=True)
        self.assertFalse(exists(note_asset))

    def test_content_pdf(self):
        note = Note(_path('womp.pdf'))
        self.assertEqual(note.content, '[PDF]')

    def test_plaintext_markdown(self):
        note = Note(_path('my note.md'))
        self.assertEqual(note.plaintext, 'HEY HI\nfoo bar qua')
