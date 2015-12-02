import os
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def watch_note(note, handle_func):
    ob = Observer()
    handler = FileSystemEventHandler()

    def handle_event(event):
        _, filename = os.path.split(event.src_path)
        if note.filename == filename or os.path.normpath(event.src_path) == os.path.normpath(note.assets):
            handle_func(note)
    handler.on_any_event = handle_event

    print('Watching {0}...'.format(note.title))
    ob.schedule(handler, note.notebook.path.abs, recursive=True)
    ob.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')
        ob.stop()
    ob.join()
