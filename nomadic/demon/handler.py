"""
Handler
=======================

Watches the notes directory for any file system
changes and responds appropriately.
"""

import os
import re
from urllib import quote

from watchdog.events import PatternMatchingEventHandler

from nomadic.core import Note, Notebook
from nomadic.util import valid_note, parsers
from nomadic.demon.logger import log

# Markdown link regex
md_link_re = re.compile(r'\[.*\]\(`?([^`\(\)]+)`?\)')

class Handler(PatternMatchingEventHandler):
    patterns = ['*'] # match everything b/c we want to match directories as well.
    ignore_patterns = ['*.build*', '*.searchindex*']

    def __init__(self, nomadic, server):
        super(Handler, self).__init__(ignore_directories=False)
        self.n = nomadic
        self.server = server

    def dispatch(self, event):
        """
        Only dispatch an event
        if it satisfies our requirements.
        """
        if event.is_directory \
        or valid_note(event.src_path) \
        and (not hasattr(event, 'dest_path') or valid_note(event.dest_path)):
            super(Handler, self).dispatch(event)

    def on_modified(self, event):
        """
        If a note's contents change...
        """
        if not event.is_directory:
            note = Note(event.src_path)
            log.debug(u'Modified: {0}'.format(note.path.rel))
            if os.path.exists(note.path.abs):
                self.n.index.update_note(note)
                self.n.builder.compile_note(note)
                self.server.refresh_clients()

    def on_created(self, event):
        """
        If a new note or notebook
        is created...
        """
        p = event.src_path

        log.debug(u'Created: {0}'.format(p))
        if not event.is_directory:
            note = Note(p)
            self.n.index.add_note(note)
            self.n.builder.compile_note(note)
        else:
            notebook = Notebook(p)
            self.n.index.update()
            self.n.builder.compile_notebook(notebook)

        # Update this note/notebook's
        # parent directory index.
        dir = os.path.dirname(p)
        parent = Notebook(dir)
        self.n.builder.index_notebook(parent)
        self.server.refresh_clients()

    def on_deleted(self, event):
        """
        If a note or notebook
        is deleted...
        """
        p = event.src_path

        log.debug(u'Deleted: {0}'.format(p))
        if not event.is_directory:
            note = Note(p)
            self.n.index.delete_note(note)
            self.n.builder.delete_note(note)
        else:
            notebook = Notebook(p)
            self.n.index.update()
            self.n.builder.delete_notebook(notebook)

        # Update this note/notebook's
        # parent directory index.
        dir = os.path.dirname(p)
        parent = Notebook(dir)
        self.n.builder.index_notebook(parent)
        self.server.refresh_clients()

    def on_moved(self, event):
        """
        If a note or notebook
        is moved...
        """
        src = event.src_path
        dest = event.dest_path

        log.debug(u'Moved: {0} to {1}'.format(src, dest))
        if not event.is_directory:
            src_note = Note(src)
            dest_note = Note(dest)

            self.n.index.delete_note(src_note)
            self.n.index.add_note(dest_note)

            self.n.builder.delete_note(src_note)
            self.n.builder.compile_note(dest_note)
        else:
            src_notebook = Notebook(src)
            dest_notebook = Notebook(dest)

            self.n.index.update()
            self.n.builder.delete_notebook(src_notebook)
            self.n.builder.compile_notebook(dest_notebook)

        # Update all references to this
        # path in any .md or .html files.
        self.update_references(src, dest)

        # Update the compiled indexes.
        for p in [src, dest]:
            dir = os.path.dirname(p)
            parent = Notebook(dir)
            self.n.builder.index_notebook(parent)
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

        for root, dirnames, filenames in self.n.rootbook.walk():
            for filename in filenames:
                path = os.path.join(root, filename)
                note = Note(path)

                update_func_ = update_func(root)
                if note.ext in ['.html', '.md']:
                    content = note.content
                    dirty = src_filename in content

                    if dirty:
                        if note.ext == '.html':
                            content = parsers.rewrite_links(content, update_func_)

                        elif note.ext == '.md':
                            for link in md_link_re.findall(content):
                                link_ = update_func_(link)
                                if link != link_:
                                    content = content.replace(link, link_)

                        note.write(content.encode('utf-8'))
                        self.n.builder.compile_note(note)

    def update_reference(self, src_filename, src_abs, dest_abs):
        def wrapper(current_dir):
            def update_func(ref):
                if src_filename not in ref: return ref
                if quote(src_filename) not in ref: return ref
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


