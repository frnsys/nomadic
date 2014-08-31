import os
import shutil
import unittest


# Everything will be relative to this test module.
path = os.path.abspath(__file__)
dir = os.path.dirname(path)

# We use a copy of the test notes directory
# so we can reset it at will.
NOTES_DIR_TEMPLATE = os.path.join(dir, u'notes')
NOTES_DIR = os.path.join(dir, u'.notes', '')
def _path(path): return os.path.join(NOTES_DIR, path)

from nomadic import conf
conf.ROOT = NOTES_DIR

class NomadicTest(unittest.TestCase):
    def __call__(self, result=None):
        """
        Sets up the tests without needing
        to call setUp.
        """
        try:
            self._pre_setup()
            super(NomadicTest, self).__call__(result)
        finally:
            self._post_teardown()

    def _pre_setup(self):
        self.notes_dir = NOTES_DIR

        if os.path.exists(NOTES_DIR):
            shutil.rmtree(NOTES_DIR)

        shutil.copytree(NOTES_DIR_TEMPLATE, NOTES_DIR)

    def _post_teardown(self):
        shutil.rmtree(NOTES_DIR)
