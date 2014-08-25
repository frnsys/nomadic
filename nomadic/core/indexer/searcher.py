"""
Searcher
=======================

Searchers through note indexes.
"""

from HTMLParser import HTMLParser
from collections import namedtuple

from colorama import Fore
from whoosh.qparser import QueryParser

Result = namedtuple('Result', ['data', 'highlights'])

def search(query, index, html=False):
    """
    Yield search results
    for a query.
    """
    with index.ix.searcher() as searcher:
        query = QueryParser('content', index.schema).parse(query)
        results = searcher.search(query, limit=None)
        results.fragmenter.charlimit = None
        results.fragmenter.surround = 100
        for result in results:
            if html:
                highlights = result.highlights('content')
            else:
                highlights = _process_highlights(result.highlights('content'))
            yield Result(result, highlights)


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

def _process_highlights(html):
    s = HighlightParser()
    s.feed(html)
    return s.get_data()
