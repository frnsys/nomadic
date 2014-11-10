from os import path
import os
import shutil

from jinja2 import Template, FileSystemLoader, environment

from nomadic.core.models import Note
from nomadic.util import md2html

dir = path.dirname(path.abspath(__file__))

env = environment.Environment()
env.loader = FileSystemLoader(path.join(dir, '../server/assets/templates'))
templ = env.get_template('presentation.html')

def compile_presentation(note, outdir):
    n = Note(note)

    # Create output directory if necessary.
    outdir = path.join(outdir, n.title)
    if not path.exists(outdir):
        os.makedirs(outdir)

    # Copy over any images.
    for img in n.images:
        img_path = path.join(outdir, img)
        img_dir = path.dirname(img_path)

        if not path.exists(img_dir):
            os.makedirs(img_dir)

        shutil.copy(path.join(n.notebook.path.abs, img), img_path)

    # Render the presentation.
    html = md2html.compile_markdown(n.content)
    content = templ.render(html=html)

    # Save it.
    with open(path.join(outdir, n.title) + '.html', 'w') as out:
        out.write(content.encode('utf-8'))

