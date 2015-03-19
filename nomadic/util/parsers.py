import os
import re
import urllib
from HTMLParser import HTMLParser

from colorama import Fore
from markdown import markdown
from lxml.html import fromstring, tostring


# Markdown regexes
md_link_re = re.compile(r'\[.*\]\(`?([^`\(\)]+)`?\)')
md_img_re = re.compile(r'!\[.*?\]\(`?([^`\(\)]+)`?\)')

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

def md_images(md):
    return [img for img in md_img_re.findall(md)]

def md_links(md):
    return [link for link in md_link_re.findall(md)]

def rewrite_links(raw_html, rewrite_func):
    """
    Take an HTML input string, rewrite links according
    to the `rewrite_func`, return the rewritten HTML string.
    """
    html = fromstring(raw_html)
    html.rewrite_links(rewrite_func)
    return tostring(html)


def rewrite_external_images(raw_html, note):
    """
    Download externally-hosted images to a note's local assets folder
    and rewrite references to those images.
    """
    rsp = note.assets
    nbp = note.notebook.path.abs

    def rewriter(link):
        link = link.split('?')[0] # split off ? params
        if link.startswith('http') and link.endswith(('.jpg', '.jpeg', '.gif', '.png')):
            if not os.path.exists(rsp):
                os.makedirs(rsp)

            ext = link.split('/')[-1].split('.')[-1]
            filename = str(hash(link)) + '.' + ext

            save_path = os.path.join(rsp, filename)

            if not os.path.exists(save_path):
                filename, _ = urllib.urlretrieve(link, save_path)

            return os.path.relpath(save_path, nbp)
        return link
    return rewrite_links(raw_html, rewriter)



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
