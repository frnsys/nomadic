import os

from nomadic.core.path import Path
from nomadic.core.note import Note
from nomadic.util import valid_notebook, valid_note


class Notebook():
    def __init__(self, path):
        self.path = Path(path)
        self.name = os.path.basename(path)


    @property
    def notebooks(self):
        for root, dirs, _ in self.walk():
            for dir in dirs:
                path = os.path.join(root, dir)
                yield Notebook(path)


    @property
    def notes(self):
        for root, dirs, files in self.walk():
            for file in files:
                path = os.path.join(root, file)
                yield Note(path)


    @property
    def contents(self):
        """
        Lists the names of all files
        and directories in this notebook,
        not recursively.
        """
        dirs = []
        files = []
        for name in os.listdir(self.path.abs):
            p = os.path.join(self.path.abs, name)
            if os.path.isfile(p):
                files.append(name)
            else:
                if valid_notebook(name):
                    dirs.append(name.decode('utf-8'))
        return dirs, files


    def walk(self):
        """
        Walks the notebook, yielding only
        valid directories and files.
        """

        for root, dirs, files in os.walk(self.path.abs):
            if valid_notebook(root):
                dirs = [d for d in dirs if valid_notebook(d)]
                files = [f for f in files if valid_note(f)]
                yield root, dirs, files
