import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension as GFM

def compile_markdown(md):
    """
    Compiles markdown to html.
    """
    return markdown.markdown(md, extensions=[GFM(), HighlightExtension()])


HIGHLIGHT_RE = r'(={2})(.+?)(={2})' # ==highlight==
class HighlightExtension(markdown.Extension):
    """An extension that supports highlighting with the <mark> tag.

    For example: ``==highlight==``.
    """

    def extendMarkdown(self, md, md_globals):
        pattern = markdown.inlinepatterns.SimpleTagPattern(HIGHLIGHT_RE, 'mark')
        md.inlinePatterns.add('nomadic-highlight', pattern, '_end')

