"""
Index
=======================

Indexes note files.
"""

import os

import click
import whoosh.index as index
from whoosh.fields import *
from whoosh.qparser import QueryParser

from nomadic.util import parsers
from nomadic.core.models import Note, Notebook, Path


schema = Schema(title=TEXT(stored=True),
        path=ID(stored=True, unique=True),
        last_mod=STORED,
        content=TEXT(stored=True))


class Index():
    def __init__(self, notes_path):
        self.notes_path = os.path.join(os.path.expanduser(notes_path), '')
        self.rootbook = Notebook(self.notes_path)
        self._prepare_index()


    @property
    def size(self):
        return self.ix.doc_count()


    def reset(self):
        """
        Indexes all of the notes.
        """
        self._prepare_index(reset=True)

        # Collect all the notes.
        notes = [note for note in self.rootbook.notes]

        # Process all the notes.
        self.add_notes(notes)


    def update(self):
        """
        Update the index with modified or new notes.
        """
        with self.ix.searcher() as searcher:
            with self.ix.writer() as writer:
                # All the note paths in the index.
                ix_paths = set()

                # The notes to re-index.
                to_index = set()

                # Loop over the stored fields in the index.
                for fields in searcher.all_stored_fields():
                    ix_path = fields['path']
                    path = Path(ix_path)

                    ix_paths.add(ix_path)

                    # If the file no longer exists...
                    if not os.path.exists(path.abs):
                        writer.delete_by_term('path', ix_path)

                    # If the file has been modified...
                    else:
                        ix_time = fields['last_mod']
                        mtime = os.path.getmtime(path.abs)

                        if mtime > ix_time:
                            # Delete the existing indexed note
                            # and queue for re-indexing.
                            writer.delete_by_term('path', ix_path)
                            to_index.add(ix_path)

                # See if there are any new files to index
                # and index queued notes.
                notes = []
                for note in self.rootbook.notes:
                    if note.path.rel in to_index or note.path.rel not in ix_paths:
                        notes.append(note)

            self.add_notes(notes)


    def search(self, query, html=False):
        """
        Yield search results for a query.
        """
        parser = parsers.HighlightParser()
        with self.ix.searcher() as searcher:
            # To prevent duplicate results.
            result_ids = []
            for field in ['content', 'title']:
                q  = QueryParser(field, self.ix.schema).parse(query)
                results = searcher.search(q, limit=None)
                results.fragmenter.charlimit = None
                results.fragmenter.surround = 100
                for result in [r for r in results if r.docnum not in result_ids]:
                    result_ids.append(result.docnum)
                    highlights = result.highlights('content')
                    note = Note(result['path'])
                    if not html:
                        parser.feed(highlights)
                        highlights = parser.get_data()
                    yield note, highlights


    def add_notes(self, notes):
        with self.ix.writer() as writer:
            with click.progressbar(notes, label='Processing notes...',
                                   fill_char=click.style('#', fg='green')) as bar:
                for note in bar:
                    writer.add_document(
                        title    = note.title,
                        path     = note.path.rel,
                        last_mod = note.last_modified,
                        content  = note.plaintext
                    )


    def add_note(self, note):
        with self.ix.writer() as writer:
            writer.add_document(
                title    = note.title,
                path     = note.path.rel,
                last_mod = note.last_modified,
                content  = note.plaintext
            )


    def delete_note(self, note):
        with self.ix.writer() as writer:
            writer.delete_by_term('path', note.path.rel)


    def update_note(self, note):
        self.delete_note(note)
        self.add_note(note)


    def note_at(self, path):
        """
        Fetching a note by path from the index.
        """
        searcher = self.ix.searcher()
        return searcher.document(path=path)


    def _prepare_index(self, reset=False):
        ix_path = os.path.join(self.notes_path, '.searchindex')

        # Load or create the index.
        if not os.path.exists(ix_path):
            os.makedirs(ix_path)
        if not index.exists_in(ix_path) or reset:
            self.ix = index.create_in(ix_path, schema)
        else:
            self.ix = index.open_dir(ix_path)
