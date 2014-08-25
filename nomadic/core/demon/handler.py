import os
import re

import lxml.html
from lxml.etree import tostring
from watchdog.events import PatternMatchingEventHandler

from nomadic.core import manager
from nomadic.core.demon.logger import log

# Markdown link regex
md_link_re = re.compile(r'\[.+\]\(`?([^`\(\)]+)`?\)')

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
        or manager.valid_note(event.src_path) \
        and (not hasattr(event, 'dest_path') or manager.valid_note(event.dest_path)):
            super(Handler, self).dispatch(event)

    def on_modified(self, event):
        """
        If a note's contents change...
        """
        if not event.is_directory:
            p = event.src_path
            log.debug('Modified: {0}'.format(p))
            if os.path.exists(p):
                self.n.index.update_note(p)
                self.n.builder.compile_note(p)
                self.server.refresh_clients()

    def on_created(self, event):
        """
        If a new note or notebook
        is created...
        """
        p = event.src_path

        log.debug('Created: {0}'.format(p))
        if not event.is_directory:
            self.n.index.add_note(p)
            self.n.builder.compile_note(p)
        else:
            # Add new notes to the index.
            self.n.index.update()
            self.n.builder.compile_notebook(p)

        # Update this note/notebook's
        # parent directory index.
        dir = os.path.dirname(p)
        self.n.builder.index_notebook(dir)
        self.server.refresh_clients()

    def on_deleted(self, event):
        """
        If a note or notebook
        is deleted...
        """
        p = event.src_path

        log.debug('Deleted: {0}'.format(p))
        if not event.is_directory:
            self.n.index.delete_note(p)
            self.n.builder.delete_note(p)
        else:
            # Remove deleted notes from the index.
            self.n.index.update()
            self.n.builder.delete_notebook(p)

        # Update this note/notebook's
        # parent directory index.
        dir = os.path.dirname(p)
        self.n.builder.index_notebook(dir)
        self.server.refresh_clients()

    def on_moved(self, event):
        """
        If a note or notebook
        is moved...
        """
        src = event.src_path
        dest = event.dest_path

        log.debug('Moved: {0} to {1}'.format(src, dest))
        if not event.is_directory:
            self.n.index.move_note(src, dest)
            self.n.builder.delete_note(src)
            self.n.builder.compile_note(dest)
        else:
            # Move the notes in the index.
            self.n.index.update()
            self.n.builder.delete_notebook(src)
            self.n.builder.compile_notebook(dest)

        # Update all references to this
        # path in any .md or .html files.
        self.update_references(src, dest)

        # Update the compiled indexes.
        for p in [src, dest]:
            dir = os.path.dirname(p)
            self.n.builder.index_notebook(dir)
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

        for root, dirnames, filenames in manager.walk(self.n.notes_path):
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
                        self.n.builder.compile_note(path)

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


