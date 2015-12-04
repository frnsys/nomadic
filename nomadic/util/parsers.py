import os
import re
from markdown import markdown
from html.parser import HTMLParser
from urllib.request import urlretrieve
from lxml.html import fromstring, tostring


# Markdown regexes
md_link_re = re.compile(r'\[.*\]\(`?([^`\(\)]+)`?\)')
md_img_re = re.compile(r'!\[.*?\]\(`?([^`\(\)]+)`?\)')


class HTMLRemover(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        self.convert_charrefs = True
        self.strict = True
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed).strip()


def remove_html(html):
    """remove html from text"""
    s = HTMLRemover()
    s.feed(html)
    return s.get_data()


def remove_md(md):
    """remove markdown markup from text"""
    html = markdown(md)
    return remove_html(html)


def md_images(md):
    """extract image references from markdown"""
    return [img for img in md_img_re.findall(md)]


def md_links(md):
    """extract links from markdown"""
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
                filename, _ = urlretrieve(link, save_path)

            return os.path.relpath(save_path, nbp)
        return link
    return rewrite_links(raw_html, rewriter)
