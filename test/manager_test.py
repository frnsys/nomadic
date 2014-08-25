import shutil
from os.path import exists

from nomadic.core import manager
from test import NomadicTest, note_at


class ManagerTest(NomadicTest):
    def test_get_note_resources_path(self):
        path = '/foo/bar/my note.md'
        resources = manager.note_resources(path)
        self.assertEqual(resources, '/foo/bar/_resources/my note/')

    def test_move_note(self):
        src = note_at('my note.md')
        dest = note_at('some_notebook/my moved note.md')

        src_resource = note_at('_resources/my note/foo.jpg')
        dest_resource = note_at('some_notebook/_resources/my moved note/foo.jpg')

        manager.move_note(src, dest)

        self.assertTrue(exists(dest))
        self.assertTrue(exists(dest_resource))

        self.assertFalse(exists(src))
        self.assertFalse(exists(src_resource))

    def test_clean_note_resources(self):
        path = note_at('my note.md')
        note_resource = note_at('_resources/my note/foo.jpg')

        self.assertTrue(exists(note_resource))

        manager.clean_note_resources(path)

        self.assertFalse(exists(note_resource))
