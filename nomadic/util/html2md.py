import re

import html2text
from lxml.html import builder, fromstring, tostring


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
    if '-evernote-highlight:true' in style or 'background-color: rgb(255, 252, 229);' in style or 'background-color: rgb(242, 250, 111);' in style:
        builders.append(highlighter)

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

def highlighter(*children):
    return builder.E('mark', *children)
