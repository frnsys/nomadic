import sys
import os
import re
from nomadic import nomadic

import html2text
from lxml.html import builder, fromstring, tostring, clean

from nomadic.util.html2md import html_to_markdown, clean_highlighted_code, highlighter
from nomadic.util import valid_notebook, valid_note
from nomadic.core.models import Note

def old_html_to_markdown(html):
    h = fromstring(html)

    clean_highlighted_code(h)
    for span in h.findall('.//span') + h.findall('.//font'):
        old_convert_span(span)

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

def old_convert_span(span):
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

# finds notes with embedded local pdfs
path = sys.argv[1]
for root, dirs, files in os.walk(path):
    if valid_notebook(root):
        for file in files:
            if valid_note(file):
                path = os.path.join(root, file)
                with open(path, 'r') as content:
                    a = old_html_to_markdown(content)
                    b = html_to_markdown(content)
                    if a != b:
                        print(path)