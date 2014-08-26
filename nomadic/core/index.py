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

from nomadic.core import Notebook, Note

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
                to_index = set()

                # Loop over the stored fields in the index.
                for fields in searcher.all_stored_fields():
                    ix_path = fields['path']
                    ix_paths.add(ix_path)

                    # If the file no longer exists...
                    if not os.path.exists(ix_path):
                        writer.delete_by_term('path', ix_path)

                    # If the file has been modified...
                    else:
                        ix_time = fields['last_mod']
                        mtime = os.path.getmtime(ix_path)

                        if mtime > ix_time:
                            # Delete the existing indexed note
                            # and queue for re-indexing.
                            writer.delete_by_term('path', ix_path)
                            to_index.add(ix_path)

                # See if there are any new files to index
                # and index queued notes.
                notes = []
                for note in self.rootbook.notes:
                    if note.path.abs in to_index or note.path.abs not in ix_paths:
                        notes.append(note)

            self.add_notes(notes)

    def search(self, query, html=False):
        """
        Yield search results for a query.
        """
        parser = HighlightParser()
        with self.ix.searcher() as searcher:
            query = QueryParser('content', self.ix.schema).parse(query)
            results = searcher.search(query, limit=None)
            results.fragmenter.charlimit = None
            results.fragmenter.surround = 100
            for result in results:
                highlights = result.highlights('content')
                if not html:
                    parser.feed(highlights)
                    highlights = parser.get_data()
                yield result, highlights

    def add_notes(self, notes):
        with self.ix.writer() as writer:
            with click.progressbar(notes, label='Processing notes...',
                                   fill_char=click.style('#', fg='green')) as bar:
                for note in bar:
                    writer.add_document(
                        title    = note.title,
                        path     = note.path.abs,
                        last_mod = note.last_modified,
                        content  = note.plaintext
                    )

    def add_note(self, path):
        with self.ix.writer() as writer:
            note = Note(path)
            writer.add_document(
                title    = note.title,
                path     = note.path.abs,
                last_mod = note.last_modified,
                content  = note.plaintext
            )

    def delete_note(self, path):
        with self.ix.writer() as writer:
            writer.delete_by_term('path', path)

    def update_note(self, path):
        self.delete_note(path)
        self.add_note(path)

    def move_note(self, src_path, dest_path):
        self.delete_note(src_path)
        self.add_note(dest_path)

    def note_at(self, path):
        """
        Convenience method for
        fetching a note by path
        from the index.
        """
        searcher = self.ix.searcher()
        return searcher.document(path=path)

    def _prepare_index(self, reset=False):
        index_path = os.path.join(self.notes_path, '.searchindex')

        # Load or create the index.
        if not os.path.exists(index_path):
            os.makedirs(index_path)
        if not index.exists_in(index_path) or reset:
            self.ix = index.create_in(index_path, schema)
        else:
            self.ix = index.open_dir(index_path)




from HTMLParser import HTMLParser
from colorama import Fore

class HighlightParser(HTMLParser):
    """
    The Whoosh highlight returns highlighted
    search words in HTML::

        <b class="match term0">keyword</b>
        <b class="match term1">keyword_two</b>

    This parser converts that markup into terminal
    color sequences so they are highlighted in the terminal.
    """
    def __init__(self):
        self.reset()
        self.fed = []
        self.highlight_encountered = False
    def handle_starttag(self, tag, attrs):
        cls = [a for a in attrs if a[0] == 'class'][0][1]
        if tag == 'b' and 'match' in cls:
            self.highlight_encountered = True
    def handle_endtag(self, tag):
        self.highlight_encountered = False
    def handle_data(self, d):
        if self.highlight_encountered:
            d = Fore.RED + d + Fore.RESET
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
