import re

import html2text
from lxml.html import builder, fromstring, tostring, clean


h2t = html2text.HTML2Text()
h2t.body_width = 0 # don't wrap lines
to_md = h2t.handle


def html_to_markdown(html):
    """
    Convert HTML to Markdown.
    This will try and convert span styling
    to the proper tags as well.

    E.g. `<span style='font-weight:bold;'>foo</span>`
    will become `<strong>foo</strong>`.
    """
    h = fromstring(html)

    clean_highlighted_code(h)
    for span in h.findall('.//span') + h.findall('.//font'):
        convert_span(span)

    html = tostring(h)

    # Not ideal but works in a pinch
    html = html.replace('<mark>', '==')
    html = html.replace('</mark>', '==')

    md = to_md(html)

    # Sometimes html2text returns a ton of extra whitespace.
    # Clean up lines with only whitespace.
    # Condense line break streaks of 3 or more.
    md = re.sub(r'\n([\s\*_]+)\n', '\n\n', md)
    md = re.sub(r'\n{3,}', '\n\n', md)

    return md


def clean_highlighted_code(html):
    """
    Strip HTML from syntax-highlighted
    code (pre and code tags).
    """
    cleaner = clean.Cleaner(allow_tags=['pre'], remove_unknown_tags=False)
    for el in html.findall('.//pre'):
        p = el.getparent()
        cleaned = cleaner.clean_html(el)
        p.replace(el, cleaned)


def convert_span(span):
    """
    Converts spans which specify
    a bold or italic style into
    strong and em tags, respectively
    (nesting them if both are specified).

    Can also handle Evernote highlighting.
    """
    p = span.getparent()

    style = span.get('style')
    if style is None:
        return

    builders = []
    if 'bold' in style:
        builders.append(builder.STRONG)
    if 'italic' in style:
        builders.append(builder.EM)
    # The latter background color rules are based on how I used to do highlighting in Evernote...
    if '-evernote-highlight:true' in style \
            or 'background-color: rgb(255, 252, 229);' in style \
            or 'background-color: rgb(242, 250, 111);' in style \
            or 'background-color: rgb(247, 252, 124);' in style \
            or 'background-color: rgb(203, 242, 254);' in style \
            or 'background-color: rgb(253, 246, 184);' in style \
            or 'background-color: rgb(242, 251, 100);' in style \
            or 'background-color: rgb(255, 248, 177);' in style \
            or 'background-color: rgb(246, 245, 154);'  in style \
            or 'background-color: rgb(255, 249, 177);' in style \
            or 'background-color: rgb(247, 250, 132);' in style \
            or 'background-color: rgb(255, 249, 173);' in style \
            or 'background-color: rgb(246, 245, 154);' in style \
            or 'background-color: rgb(255, 211, 227);' in style \
            or 'background-color:rgb(255, 250, 165);' in style \
            or 'background-color: rgb(255, 255, 204);' in style:

        builders.append(highlighter)

    tail = span.tail
    if builders:
        children = []
        if span.text is not None:
            children.append(span.text)
        for c in span.getchildren():
            children.append(c)
            if c.tail is not None and c.tail.strip():
                # Have to wrap the tail text in a span tag,
                # or else it won't get added.
                children.append(builder.SPAN(c.tail))

        # Recursively apply the builders.
        el = builders[0](*children)
        for b in builders[1:]:
            el = b(el)

        # Replace the old element with the new one.
        p.replace(span, el)

        # Insert other text.
        if tail is not None and tail.strip():
            p.insert(p.index(el) + 1, builder.SPAN(tail))

def highlighter(*children):
    return builder.E('mark', *children)
