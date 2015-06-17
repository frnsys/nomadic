import re
import markdown
from markdown.inlinepatterns import SimpleTagPattern, ImagePattern
from markdown.util import etree
from mdx_gfm import GithubFlavoredMarkdownExtension as GFM


def compile_markdown(md):
    """
    Compiles markdown to html.
    """

    mjh = MathJaxHandler()
    md = mjh.extract(md)
    md = markdown.markdown(md, extensions=[GFM(), NomadicMD(), 'markdown.extensions.footnotes'], lazy_ol=False)
    return mjh.restore(md)



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
    PDF_RE = r'\!\[(.*)\]\(`?(?:<.*>)?([^`\(\)]+pdf)(?:</.*>)?`?\)' # ![...](path/to/something.pdf)

    def extendMarkdown(self, md, md_globals):
        highlight_pattern = SimpleTagPattern(self.HIGHLIGHT_RE, 'mark')
        md.inlinePatterns.add('highlight', highlight_pattern, '_end')

        pdf_pattern = PDFPattern(self.PDF_RE)
        md.inlinePatterns.add('pdf_link', pdf_pattern, '_begin')


class MathJaxHandler():
    """
    This extracts all MathJax from the markdown and re-injects it after
    markdown processing is finished. This is so markdown doesn't mess with it.

    There might be a better way of handling MathJax buuuut this will do for now.
    """
    # matching `:: ::`, ignoring anything in backticks.
    MATHJAX_RE = re.compile(r'(?<!`)[\:\$]{2}.+?[\:\$]{2}(?!`)', re.DOTALL)
    PLACEHOLDER = '<MATHJAXHOLDER>'

    def extract(self, doc):
        self.formulae = []

        for match in self.MATHJAX_RE.findall(doc):
            self.formulae.append(match)
            doc = doc.replace(match, self.PLACEHOLDER)
        return doc


    def restore(self, doc):
        for i, match in enumerate(re.findall(self.PLACEHOLDER, doc)):
            doc = str.replace(doc, match, self.formulae[i], 1)
        return doc
