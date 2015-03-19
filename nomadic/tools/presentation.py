from os import path
import os
import shutil

from jinja2 import Template, FileSystemLoader, environment

from nomadic.util import md2html

dir = path.dirname(path.abspath(__file__))

env = environment.Environment()
env.loader = FileSystemLoader(path.join(dir, '../server/assets/templates'))
templ = env.get_template('presentation.html')

def compile_presentation(note, outdir):
    n = note

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

import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

def watch_presentation(note, outdir):
    n = note

    ob      = Observer()
    handler = FileSystemEventHandler()

    def handle_event(event):
        _, filename = path.split(event.src_path)
        if n.filename == filename or path.normpath(event.src_path) == path.normpath(n.assets):
            compile_presentation(n, outdir)
    handler.on_any_event = handle_event

    print('Watching {0}...'.format(n.title))
    ob.schedule(handler, n.notebook.path.abs, recursive=True)
    ob.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')
        ob.stop()
    ob.join()
