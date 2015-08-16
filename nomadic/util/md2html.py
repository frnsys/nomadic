import markdown
from markdown.inlinepatterns import SimpleTagPattern, ImagePattern
from markdown.util import etree
from mdx_gfm import GithubFlavoredMarkdownExtension as GFM


def compile_markdown(md):
    """
    Compiles markdown to html.
    """
    return markdown.markdown(md, extensions=[GFM(), NomadicMD(), MathJaxExtension(), 'markdown.extensions.footnotes'], lazy_ol=False)



class PDFPattern(ImagePattern):
    def handleMatch(self, m):
        src = m.group(3)
        fig = etree.Element('figure')

        obj = etree.SubElement(fig, 'iframe')
        obj.set('src', src)

        a = etree.SubElement(fig, 'a')
        a.set('href', src)
        a.text = m.group(2) or src.split('/')[-1]

        return fig


class NomadicMD(markdown.Extension):
    """
    An extension that supports:
    - highlighting with the <mark> tag.
    - pdf embedding with the <iframe> tag.
    """
    HIGHLIGHT_RE = r'(={2})(.+?)(={2})' # ==highlight==
    PDF_RE = r'\!\[([^\[\]]*)\]\(`?(?:<.*>)?([^`\(\)]+pdf)(?:</.*>)?`?\)' # ![...](path/to/something.pdf)

    def extendMarkdown(self, md, md_globals):
        highlight_pattern = SimpleTagPattern(self.HIGHLIGHT_RE, 'mark')
        md.inlinePatterns.add('highlight', highlight_pattern, '_end')

        pdf_pattern = PDFPattern(self.PDF_RE)
        md.inlinePatterns.add('pdf_link', pdf_pattern, '_begin')


"""
From <https://github.com/mayoff/python-markdown-mathjax>
"""
class MathJaxPattern(markdown.inlinepatterns.Pattern):
    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node

class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')
