import os
import shutil

from nomad.indexer import Index
from test import NomadTest, note_at


class IndexerTest(NomadTest):
    def setUp(self):
        self.index = Index(self.notes_dir)
        self.index.reset()
        self.expected_notes = 6

    def test_reset_index(self):
        index_path = os.path.join(self.notes_dir, u'.searchindex')
        shutil.rmtree(index_path)

        self.index.reset()

        self.assertEqual(self.index.size, self.expected_notes)

    def test_update_index(self):
        with open(note_at('new note.md'), 'w') as new_note:
            new_note.write('foobar')

        self.index.update()

        self.assertEqual(self.index.size, self.expected_notes + 1)

    def test_add_note(self):
        path = note_at('new note.md')
        with open(path, 'w') as new_note:
            new_note.write('foobar')

        self.index.add_note(path)

        self.assertEqual(self.index.size, self.expected_notes + 1)

    def test_delete_note(self):
        path = note_at('my note.md')
        self.index.delete_note(path)
        self.assertEqual(self.index.size, self.expected_notes - 1)

        self.assertTrue(not self.index.note_at(path))

    def test_update_note(self):
        path = note_at('my note.md')
        with open(path, 'w') as note:
            note.write(u'changed note content')

        self.index.update_note(path)

        note_ = self.index.note_at(path)
        self.assertTrue(note_)
        self.assertEqual(note_['content'], u'changed note content')

    def test_move_note(self):
        src = note_at('my note.md')
        dest = note_at('my note moved.md')

        self.assertTrue(self.index.note_at(src))

        shutil.move(src, dest)
        self.index.move_note(src, dest)

        self.assertTrue(not self.index.note_at(src))
        self.assertTrue(self.index.note_at(dest))


