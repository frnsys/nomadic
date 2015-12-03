import time
from watchdog.observers import Observer
from nomadic.util import logger
from nomadic.server import Server
from nomadic.demon.handler import Handler


def start(nomadic, port):
    """start the daemon;
    i.e. run the server and the file system handler/watcher"""
    logger.log.debug('nomadic daemon started.')
    try:
        ob = Observer()
        srvr = Server(port)
        hndlr = Handler(nomadic, srvr)

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
