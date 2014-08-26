from nomadic.core.note import Note
from nomadic.core.notebook import Notebook
from nomadic.core import index, build

class Nomadic():
    def __init__(self, notes_path):
        self.notes_path = notes_path
        self.rootbook = Notebook(notes_path)
        self.index = index.Index(notes_path)
        self.builder = build.Builder(notes_path)
