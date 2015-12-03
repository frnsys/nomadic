import re
from markdown import markdown
from html.parser import HTMLParser


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
