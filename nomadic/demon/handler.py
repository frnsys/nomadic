"""
Handler
=======================

Watches the notes directory for any file system
changes and responds appropriately.
"""

import os
import shutil
from urllib.parse import quote
from watchdog.events import PatternMatchingEventHandler
from nomadic.util import valid_note, parsers, logger
from nomadic.core.models import Note


class Handler(PatternMatchingEventHandler):
    # Match everything b/c we want to match directories as well.
    patterns = ['*']
    ignore_patterns = ['*.build*']

    def __init__(self, nomadic, server):
        super().__init__(ignore_directories=False)
        self.n = nomadic
        self.server = server

    def dispatch(self, event):
        """
        Only dispatch an event if it satisfies our requirements.
        """
        if event.is_directory \
        or valid_note(event.src_path) \
        and (not hasattr(event, 'dest_path') or valid_note(event.dest_path)):
            super().dispatch(event)

    def on_created(self, event):
        p = event.src_path
        logger.log.debug('Created: {0}'.format(p))
        if not event.is_directory:
            # reload note clients to reflect changes
            self.server.refresh_clients()

    def on_moved(self, event):
        src = event.src_path
        dest = event.dest_path

        logger.log.debug('Moved: {0} to {1}'.format(src, dest))
        if not event.is_directory:
            src_note = Note(src)
            dest_note = Note(dest)

            if os.path.exists(src_note.assets):
                shutil.move(src_note.assets, dest_note.assets)

        # update all references to this
        # path in any .md files.
        self.update_references(src, dest)

    # TO DO:
    # might need a separate daemon/watcher for this
    # since a file of any type, not just md/txt/pdf,
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

        for root, notebooks, notes in self.n.rootbook.walk():
            for note in notes:
                update_func_ = update_func(root)
                content = note.content
                dirty = src_filename in content

                if dirty:
                    if note.ext == '.md':
                        for link in parsers.md_links(content):
                            link_ = update_func_(link)
                            if link != link_:
                                content = content.replace(link, link_)

                    note.write(content.encode('utf-8'))

    def update_reference(self, src_filename, src_abs, dest_abs):
        def wrapper(current_dir):
            def update_func(ref):
                if src_filename not in ref and quote(src_filename) not in ref: return ref
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


