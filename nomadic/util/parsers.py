from HTMLParser import HTMLParser

from colorama import Fore
from markdown import markdown
from lxml.html import fromstring, tostring


class HTMLRemover(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed).strip()


def remove_html(html):
    s = HTMLRemover()
    s.feed(html)
    return s.get_data()


def remove_md(md):
    html = markdown(md)
    return remove_html(html)


def rewrite_links(raw_html, rewrite_func):
    """
    Take an HTML input string, rewrite links according
    to the `rewrite_func`, return the rewritten HTML string.
    """
    html = fromstring(raw_html)
    html.rewrite_links(rewrite_func)
    return tostring(html)


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
