from collections import namedtuple
from nomadic.core import Nomadic
from nomadic.demon.handler import Handler
from tests import NomadicTest, _path

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
        self.handler = Handler(self.nomadic)

    def test_update_references_markdown(self):
        path = _path('some_notebook/a cool note.md')

        ref = _path('some_notebook/nested book/empty.md')
        ref_new = _path('moved empty note.md')

        rel_link = 'nested book/empty.md'
        rel_link_new = '../moved empty note.md'

        with open(path, 'r') as note:
            note_content = note.read()
            self.assertTrue(rel_link in note_content)
            self.assertFalse(rel_link_new in note_content)

        self.handler.update_references(ref, ref_new)

        with open(path, 'r') as note:
            note_content = note.read()
            self.assertFalse(rel_link in note_content)
            self.assertTrue(rel_link_new in note_content)
