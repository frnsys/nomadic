"""
Extractor
=======================

Extracts data from note files.
"""

import os
from StringIO import StringIO
from HTMLParser import HTMLParser
from collections import namedtuple

import click
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from markdown import markdown

Note = namedtuple('Note', ['title', 'ext', 'path'])

def process_notes(notes):
    """
    Process multiple Notes.
    """
    with click.progressbar(notes, label='Processing notes...',
                           fill_char=click.style('#', fg='green')) as bar:
        for note in bar:
            yield process_note(note)

def process_note(note):
    """
    Process a single Note.
    """
    return {
        'title':    note.title,
        'path':     note.path,
        'content':  extract_note_content(note),
        'last_mod': os.path.getmtime(note.path)
    }

def note_from_path(path):
    """
    Returns a Note object
    for a given path.
    """
    if type(path) is str:
        path = path.decode('utf-8')

    _, filename = os.path.split(path)
    title, ext = os.path.splitext(filename)
    return Note(title, ext, path)

def extract_note_content(note):
    """
    Extracts text content
    from a note, returning a unicode str.
    """
    if note.ext == '.pdf':
        content = _extract_pdf_text(note.path).decode('utf-8')
    else:
        with open(note.path, 'rb') as f:
            content = f.read().decode('utf-8')
            if note.ext == '.html':
                content = _remove_html(content)
            elif note.ext == '.md':
                content = _remove_md(content)
    if type(content) is str:
        content = content.decode('utf-8')
    return content

def _extract_pdf_text(pdf_file):
    rsrcmgr = PDFResourceManager(caching=True)
    outp = StringIO()
    device = TextConverter(rsrcmgr, outp, codec='utf-8', laparams=LAParams())
    with open(pdf_file, 'rb') as f:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(f, set(), maxpages=0, caching=True, check_extractable=True):
            interpreter.process_page(page)
    device.close()
    text = outp.getvalue()
    outp.close()
    return text.strip()

class HTMLRemover(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed).strip()

def _remove_html(html):
    s = HTMLRemover()
    s.feed(html)
    return s.get_data()

def _remove_md(md):
    html = markdown(md)
    return _remove_html(html)
