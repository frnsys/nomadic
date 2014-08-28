import os

from nomadic import conf

class Path():
    def __init__(self, path):
        if isinstance(path, str):
            path = path.decode('utf-8')

        if os.path.isabs(path):
            self.abs = path
            self.rel = os.path.relpath(path, conf.ROOT)
        else:
            self.rel = path
            self.abs = os.path.join(conf.ROOT, path)
