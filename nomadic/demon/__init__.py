"""
Demon
=======================

Manages the filesystem handler
and background server.
"""

import sys
import time

from watchdog.observers import Observer
from daemon import DaemonContext

from nomadic.demon import server, handler, logger

def start(nomadic, port, debug=False):
    logger.log.debug('nomadic daemon started.')

    if debug:
        summon(nomadic, port)

    else:
        with DaemonContext(stdout=sys.stdout):
            summon(nomadic, port)

def summon(nomadic, port):
    try:
        ob = Observer()
        srvr = server.Server(nomadic, port)
        hndlr = handler.Handler(nomadic, srvr)
        ob.schedule(hndlr, nomadic.notes_path, recursive=True)
        ob.start()
        srvr.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ob.stop()

        ob.join()
    except Exception as e:
        logger.log.exception(e)
        raise
    else:
        ob.stop()
        ob.join()
