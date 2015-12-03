from nomadic.core.models import Note, Notebook
from nomadic.core.search import search, search_pdf


class Nomadic():
    def __init__(self, notes_path):
        self.notes_path = notes_path
        self.rootbook = Notebook(notes_path)

    def search(self, query, delimiters=('<b>','</b>'), window=150):
        """search across txt/md and pdf files
        window -> num characters to show before/after match
        delimiters -> what to surround matches with
        """

        results = []
        for note_path, matches in search(query).items():
            note = Note(note_path)
            highlights = []
            # results.append((Note(note_path), [text for text, _ in matches]))
            for text, positions in matches:
                for start, end in positions:
                    frm = max(0, start - window)
                    to = min(len(text), start + end + window)
                    # TODO this isn't quite right
                    # it may be because positions are based on byte string
                    # representation and not unicode?
                    snippet = text[frm:start] + delimiters[0] + text[start:start+end] + delimiters[1] + text[start+end:to]

                    if frm > 0:
                        snippet = '...{}'.format(snippet)
                    if to < len(text):
                        snippet = '{}...'.format(snippet)
                    highlights.append(snippet)
            results.append((note, highlights))

        # we don't get match positions for pdfs, unfortunately
        for note_path, matches in search_pdf(query, window).items():
            note = Note(note_path)
            results.append((note, matches))
        return results
