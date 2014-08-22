import os

def walk(notes_dir):
    """
    Walk a notes directory,
    yielding only for valid directories.
    """
    for root, dirnames, filenames in os.walk(notes_dir):
        if valid_notebook(root):
            yield root, dirnames, filenames

def valid_notebook(dir):
    """
    We want to ignore the build and searchindex
    as well as all resource directories.
    """
    if '.build' in dir: return False
    if '.searchindex' in dir: return False
    if '_resources' in dir: return False
    return True
