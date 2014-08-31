import os
import shutil

from nomadic.core import Note, Index
from test import NomadicTest, _path


class IndexTest(NomadicTest):
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
        with open(_path('new note.md'), 'w') as new_note:
            new_note.write('foobar')

        self.index.update()

        self.assertEqual(self.index.size, self.expected_notes + 1)

    def test_add_note(self):
        note = Note(_path('new note.md'))
        note.write('foobar')

        self.index.add_note(note)

        self.assertEqual(self.index.size, self.expected_notes + 1)

    def test_delete_note(self):
        note = Note(_path('my note.md'))
        self.index.delete_note(note)
        self.assertEqual(self.index.size, self.expected_notes - 1)

        self.assertTrue(not self.index.note_at(note.path.rel))

    def test_update_note(self):
        note = Note(_path('my note.md'))
        note.write(u'changed note content')

        self.index.update_note(note)

        note_ = self.index.note_at(note.path.rel)
        self.assertTrue(note_)
        self.assertEqual(note_['content'], u'changed note content')

    def test_search(self):
        results = [result for result in self.index.search('hullo')]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].path.rel, 'some_notebook/a cool note.md')


