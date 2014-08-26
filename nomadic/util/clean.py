from HTMLParser import HTMLParser

from markdown import markdown

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
