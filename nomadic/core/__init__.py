from nomadic.core.note import Note
from nomadic.core.notebook import Notebook
from nomadic.core.index import Index
from nomadic.core.build import Builder

class Nomadic():
    def __init__(self, notes_path):
        self.notes_path = notes_path
        self.rootbook = Notebook(notes_path)
        self.index = Index(notes_path)
        self.builder = Builder(notes_path)
