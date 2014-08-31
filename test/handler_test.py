import os
import shutil
from urllib import quote
from collections import namedtuple

from nomadic.core import Nomadic, Note
from nomadic.demon.handler import Handler
from test import NomadicTest, _path

# Mock the watchdog events.
Event = namedtuple('Event', ['is_directory', 'src_path', 'dest_path'])

class HandlerTest(NomadicTest):
    """
    This tests the handler's handling of
    events, but does not test
    the triggering of those events.
    (We're just assuming that the
    watchdog lib has got it covered!)

    So we do all the file handling
    and manually trigger the proper response.
    """
    def setUp(self):
        self.nomadic = Nomadic(self.notes_dir)
        self.nomadic.index.reset()

        self.handler = Handler(self.nomadic)

    def test_on_created(self):
        note = Note(_path('a new note.md'))
        note.write('# a new note')

        e = Event(is_directory=False, src_path=note.path.abs, dest_path=None)
        self.handler.on_created(e)

        self.assertTrue(self.nomadic.index.note_at(note.path.rel))

    def test_on_deleted(self):
        note = Note(_path('my note.md'))

        self.assertTrue(self.nomadic.index.note_at(note.path.rel))

        os.remove(note.path.abs)
        e = Event(is_directory=False, src_path=note.path.abs, dest_path=None)
        self.handler.on_deleted(e)

        self.assertFalse(self.nomadic.index.note_at(note.path.rel))

    def test_on_modified(self):
        note = Note(_path('my note.md'))

        note.write('a changed note')

        e = Event(is_directory=False, src_path=note.path.abs, dest_path=None)
        self.handler.on_modified(e)

        note = self.nomadic.index.note_at(note.path.rel)
        self.assertEqual('a changed note', note['content'])

    def test_on_moved(self):
        note = Note(_path('my note.md'))

        note_new = Note(_path('some_notebook/my moved note.md'))

        self.assertTrue(self.nomadic.index.note_at(note.path.rel))

        shutil.move(note.path.abs, note_new.path.abs)
        e = Event(is_directory=False, src_path=note.path.abs, dest_path=note_new.path.abs)
        self.handler.on_moved(e)

        self.assertFalse(self.nomadic.index.note_at(note.path.rel))
        self.assertTrue(self.nomadic.index.note_at(note_new.path.rel))

    def test_on_deleted_directory(self):
        path = _path('some_notebook')

        shutil.rmtree(path)
        e = Event(is_directory=True, src_path=path, dest_path=None)
        self.handler.on_deleted(e)

        self.assertFalse(self.nomadic.index.note_at(_path('some_notebook/a cool note.md')))

    def test_on_moved_directory(self):
        path = _path('some_notebook')
        path_new = _path('moved_notebook')

        shutil.move(path, path_new)
        e = Event(is_directory=True, src_path=path, dest_path=path_new)
        self.handler.on_moved(e)

        old_note = Note(_path('some_notebook/a cool note.md'))
        self.assertFalse(self.nomadic.index.note_at(old_note.path.rel))

        new_note = Note(_path('moved_notebook/a cool note.md'))
        self.assertTrue(self.nomadic.index.note_at(new_note.path.rel))

    def test_update_references_markdown(self):
        path = _path('some_notebook/a cool note.md')

        ref = _path('some_notebook/nested book/empty.md')
        ref_new = _path('moved empty note.md')

        rel_link = 'nested book/empty.md'
        rel_link_ = quote('nested book/empty.html')
        rel_link_new = '../moved empty note.md'
        rel_link_new_ = quote('../moved empty note.html')

        with open(path, 'r') as note:
            note_content = note.read()
            self.assertTrue(rel_link in note_content)
            self.assertFalse(rel_link_new in note_content)

        self.handler.update_references(ref, ref_new)

        with open(path, 'r') as note:
            note_content = note.read()
            self.assertFalse(rel_link in note_content)
            self.assertTrue(rel_link_new in note_content)

    def test_update_references_html(self):
        path = _path('another note.html')

        ref = _path('some_notebook/a cool note.md')
        ref_new = _path('moved cool note.md')

        rel_link = 'some_notebook/a cool note.md'
        rel_link_ = quote('some_notebook/a cool note.html')
        rel_link_new = quote('moved cool note.md')
        rel_link_new_ = quote('moved cool note.html')

        with open(path, 'r') as note:
            note_content = note.read()
            self.assertTrue(rel_link in note_content)
            self.assertFalse(rel_link_new in note_content)

        self.handler.update_references(ref, ref_new)

        with open(path, 'r') as note:
            note_content = note.read()
            self.assertFalse(rel_link in note_content)
            self.assertTrue(rel_link_new in note_content)
