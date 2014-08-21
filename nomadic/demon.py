"""
Demon
=======================

A daemon which monitors the notebook
directory and manages indexing/compiling.
"""

import os
import re
import sys
import time
import logging

import lxml.html
from lxml.etree import tostring
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from daemon import DaemonContext

# Markdown link regex
md_link_re = re.compile(r'\[.+\]\(`?([^`\(\)]+)`?\)')

logger = logging.getLogger('nomadic_daemon')
logger.setLevel( logging.DEBUG )
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

from nomadic import indexer, builder, server


def start(note_path, debug=False):
    logger.debug('NomadicDaemon started.')

    if debug:
        observe(note_path)

    else:
        with DaemonContext(stdout=sys.stdout):
            observe(note_path)

def observe(note_path):
    try:
        ob = Observer()
        d = NomadicDaemon(note_path)
        ob.schedule(d, note_path, recursive=True)
        ob.start()
        d.server.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ob.stop()

        ob.join()
    except Exception as e:
        logger.exception(e)
        raise
    else:
        ob.stop()
        ob.join()

class NomadicDaemon(PatternMatchingEventHandler):
    patterns = ['*'] # match everything b/c we want to match directories as well.
    ignore_patterns = ['*.build*', '*.searchindex*']
    valid_exts = ('.html', '.md', '.txt', '.pdf')

    def __init__(self, note_path):
        super(NomadicDaemon, self).__init__(ignore_directories=False)
        self.index = indexer.Index(note_path)
        self.builder = builder.Builder(note_path)
        self.server = server.Server(self.index, self.builder)
        self.notes_path = note_path

    def dispatch(self, event):
        """
        Only dispatch an event
        if it satisfies our requirements.
        """
        if event.is_directory \
        or event.src_path.endswith(self.valid_exts) \
        and (not hasattr(event, 'dest_path') or event.dest_path.endswith(self.valid_exts)):
            super(NomadicDaemon, self).dispatch(event)

    def on_modified(self, event):
        """
        If a note's contents change...
        """
        if not event.is_directory:
            p = event.src_path
            logger.debug('Modified: {0}'.format(p))
            self.index.update_note(p)
            self.builder.compile_note(p)
            self.server.refresh_clients()

    def on_created(self, event):
        """
        If a new note or notebook
        is created...
        """
        p = event.src_path

        logger.debug('Created: {0}'.format(p))
        if not event.is_directory:
            self.index.add_note(p)
            self.builder.compile_note(p)
        else:
            # Add new notes to the index.
            self.index.update()
            self.builder.compile_notebook(p)

        # Update this note/notebook's
        # parent directory index.
        dir = os.path.dirname(p)
        self.builder.index_notebook(dir)
        self.server.refresh_clients()

    def on_deleted(self, event):
        """
        If a note or notebook
        is deleted...
        """
        p = event.src_path

        logger.debug('Deleted: {0}'.format(p))
        if not event.is_directory:
            self.index.delete_note(p)
            self.builder.delete_note(p)
        else:
            # Remove deleted notes from the index.
            self.index.update()
            self.builder.delete_notebook(p)

        # Update this note/notebook's
        # parent directory index.
        dir = os.path.dirname(p)
        self.builder.index_notebook(dir)
        self.server.refresh_clients()

    def on_moved(self, event):
        """
        If a note or notebook
        is moved...
        """
        src = event.src_path
        dest = event.dest_path

        logger.debug('Moved: {0} to {1}'.format(src, dest))
        if not event.is_directory:
            self.index.move_note(src, dest)
            self.builder.delete_note(src)
            self.builder.compile_note(dest)
        else:
            # Move the notes in the index.
            self.index.update()
            self.builder.delete_notebook(src)
            self.builder.compile_notebook(dest)

        # Update all references to this
        # path in any .md or .html files.
        self.update_references(src, dest)

        # Update the compiled indexes.
        for p in [src, dest]:
            dir = os.path.dirname(p)
            self.builder.index_notebook(dir)
        self.server.refresh_clients()

    # TO DO:
    # might need a separate daemon/watcher for this
    # since a file of any type, not just html/md/txt/pdf,
    # could be referenced and moved.
    def update_references(self, src, dest):
        """
        Update at all references to the
        `src` path with the `dest` path.
        """
        src_abs = os.path.abspath(src)
        dest_abs = os.path.abspath(dest)
        _, src_filename = os.path.split(src)
        update_func = self.update_reference(src_filename, src_abs, dest_abs)

        for root, dirnames, filenames in indexer.walk_notes(self.notes_path):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                path = os.path.join(root, filename)

                update_func_ = update_func(root)
                if ext in ['.html', '.md']:
                    with open(path, 'r') as note:
                        content = note.read()
                        dirty = src_filename in content

                    if dirty:
                        if ext == '.html':
                            html = lxml.html.fromstring(content)
                            html.rewrite_links(update_func_)
                            content = tostring(html)

                        elif ext == '.md':
                            for link in md_link_re.findall(content):
                                link_ = update_func_(link)
                                if link != link_:
                                    content = content.replace(link, link_)

                        with open(path, 'w') as note:
                            note.write(content.encode('utf-8'))
                        self.builder.compile_note(path)

    def update_reference(self, src_filename, src_abs, dest_abs):
        def wrapper(current_dir):
            def update_func(ref):
                if src_filename not in ref: return ref
                if '://' in ref: return ref

                if os.path.isabs(ref):
                    ref.replace(src_abs, dest_abs)
                else:
                    abs_ref = os.path.join(current_dir, ref)
                    new_abs_ref = abs_ref.replace(src_abs, dest_abs)
                    ref = os.path.relpath(new_abs_ref, current_dir)
                return ref
            return update_func
        return wrapper


