import html2text
from lxml.html import builder, fromstring, tostring

to_md = html2text.HTML2Text().handle
def html_to_markdown(html):
    """
    Convert HTML to Markdown.
    This will try and convert span styling
    to the proper tags as well.

    E.g. `<span style='font-weight:bold;'>foo</span>`
    will become `<strong>foo</strong>`.
    """
    h = fromstring(html)
    for span in h.findall('.//span'):
        convert_span(span)
    html = tostring(h)

    return to_md(html)

def convert_span(span):
    """
    Converts spans which specify
    a bold or italic style into
    strong and em tags, respectively
    (nesting them if both are specified).
    """
    p = span.getparent()

    style = span.get('style')
    builders = []
    if 'bold' in style:
        builders.append(builder.STRONG)
    if 'italic' in style:
        builders.append(builder.EM)

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
