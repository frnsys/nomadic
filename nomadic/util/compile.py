import os
import shutil
from jinja2 import FileSystemLoader, environment
from nomadic.util import md2html


dir = os.path.dirname(os.path.abspath(__file__))
env = environment.Environment()
env.loader = FileSystemLoader(os.path.join(dir, '../server/assets/templates/export'))


def compile_note(note, outdir, templ):
    templ = env.get_template('{}.html'.format(templ))

    # create output directory if necessary
    outdir = os.path.join(outdir, note.title)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # copy over any images
    for img in note.images:
        img_path = os.path.join(outdir, img)
        img_dir = os.path.dirname(img_path)

        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        shutil.copy(os.path.join(note.notebook.path.abs, img), img_path)

    # render the presentation
    html = md2html.compile_markdown(note.content)
    content = templ.render(html=html)

    # save it
    with open(os.path.join(outdir, note.title) + '.html', 'w') as out:
        out.write(content)
