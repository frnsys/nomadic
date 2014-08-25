from nomadic.core import indexer, builder

class Nomadic():
    def __init__(self, notes_path):
        self.notes_path = notes_path
        self.index = indexer.Index(notes_path)
        self.builder = builder.Builder(notes_path)
