import html
from nomadic.core.models import Note, Notebook
from nomadic.core.search import search, search_pdf


class Nomadic():
    def __init__(self, notes_path):
        self.notes_path = notes_path
        self.rootbook = Notebook(notes_path)

    def search(self, query, delimiters=('<b>','</b>'), window=150, include_pdf=False, html_out=False):
        """search across txt/md and pdf files
        window -> num characters to show before/after match
        delimiters -> what to surround matches with
        html_out -> whether or not output will be to html
        """
        results = []
        for note_path, matches in search(query).items():
            note = Note(note_path)
            highlights = []
            for text, positions in matches:
                for start, end in positions:
                    frm = max(0, start - window)
                    to = min(len(text), start + end + window)
                    snippet = \
                        self._process(text[frm:start], escape=html_out) + \
                        delimiters[0] + \
                        self._process(text[start:start+end], escape=html_out) + \
                        delimiters[1] + \
                        self._process(text[start+end:to], escape=html_out)

                    if frm > 0:
                        snippet = '...{}'.format(snippet)
                    if to < len(text):
                        snippet = '{}...'.format(snippet)
                    highlights.append(snippet)
            results.append((note, highlights))

        if include_pdf:
            # we don't get match positions for pdfs, unfortunately
            for note_path, matches in search_pdf(query, window).items():
                note = Note(note_path)
                results.append((note, matches))
        return results

    def _process(text, escape=False):
        text = text.decode('utf-8')
        return html.escape(text) if escape else text
