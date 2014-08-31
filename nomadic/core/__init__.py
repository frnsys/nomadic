from nomadic.core.models import Note, Notebook
from nomadic.core.index import Index

class Nomadic():
    def __init__(self, notes_path):
        self.notes_path = notes_path
        self.rootbook = Notebook(notes_path)
        self.index = Index(notes_path)
