import os
import re
import shutil
from urllib import quote
from nomadic.util import html2md

def port_evernote(path, to_notebook):
    """
    Ports an exported Evernote html note to a nomadic markdown note,
    porting over the resources folder (if there is one)
    and updating references to it.
    """
    path = path.decode('utf-8')
    basepath, filename = os.path.split(path)
    title, ext = os.path.splitext(filename)

    # Look for an Evernote resources directory.
    abspath = os.path.abspath(path)
    dirname = os.path.dirname(abspath)
    en_rsrc_rel = u'{0}.resources'.format(title)
    en_rsrc_abs = os.path.join(dirname, en_rsrc_rel)

    with open(path, 'r') as html_file:
        html = html_file.read()

    n_rsrc_rel = u'assets/{0}'.format(title)
    n_rsrc_abs = os.path.join(to_notebook.path.abs, n_rsrc_rel)

    if os.path.exists(en_rsrc_abs):
        shutil.move(en_rsrc_abs, n_rsrc_abs)

    markdown = html2md.html_to_markdown(html)

    # Update asset references.
    markdown = markdown.replace(en_rsrc_rel, quote(n_rsrc_rel.encode('utf-8')))
    markdown = markdown.replace(quote_evernote(en_rsrc_rel), quote(n_rsrc_rel.encode('utf-8')))

    path = os.path.join(to_notebook.path.abs, title + '.md')
    with open(path, 'w') as note:
        note.write(markdown.encode('utf-8'))

    return path

def quote_evernote(text):
    return quote(text.encode('utf-8'), safe='@+!,&?\'()').replace('(', '\(').replace(')', '\)').replace('[', '\[').replace(']', '\]')
