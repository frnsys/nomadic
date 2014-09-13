import markdown
from markdown.inlinepatterns import SimpleTagPattern, ImagePattern
from markdown.util import etree
from mdx_gfm import GithubFlavoredMarkdownExtension as GFM


def compile_markdown(md):
    """
    Compiles markdown to html.
    """
    # toc = table of contents extension
    return markdown.markdown(md, extensions=[GFM(), NomadicMD()], lazy_ol=False)


HIGHLIGHT_RE = r'(={2})(.+?)(={2})' # ==highlight==
PDF_RE = r'\!\[(.*)\]\(`?(?:<.*>)?([^`\(\)]+pdf)(?:</.*>)?`?\)' # ![...](path/to/something.pdf)

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
    def extendMarkdown(self, md, md_globals):
        highlight_pattern = SimpleTagPattern(HIGHLIGHT_RE, 'mark')
        md.inlinePatterns.add('highlight', highlight_pattern, '_end')

        pdf_pattern = PDFPattern(PDF_RE)
        md.inlinePatterns.add('pdf_link', pdf_pattern, '_begin')
