import os

VALID_EXTS = ('.html', '.md', '.pdf', '.txt')

def walk(notes_dir):
    """
    Walk a notes directory,
    yielding only for valid directories.
    """
    for root, dirs, files in os.walk(notes_dir):
        if valid_notebook(root):
            dirs = [d for d in dirs if valid_notebook(d)]
            files = [f for f in files if valid_note(f)]
            yield root, dirs, files

def filenames(path):
        """
        Lists all files and directories
        in this path, NOT recursive.
        It does not return their paths,
        just their names.
        """
        dirs = []
        files = []
        for name in os.listdir(path):
            p = os.path.join(path, name)
            if os.path.isfile(p):
                files.append(name)
            else:
                if valid_notebook(name):
                    dirs.append(name.decode('utf-8'))
        return dirs, files

def valid_notebook(path):
    """
    We want to ignore the build and searchindex
    as well as all resource directories.
    """
    if '.build' in path: return False
    if '.searchindex' in path: return False
    if '_resources' in path: return False
    return True

def valid_note(path):
    """
    Only certain filetypes qualify as notes,
    and we want to ignore ones named 'index.html'
    since they may be build indexes.
    """
    return path.endswith(VALID_EXTS) and 'index.html' not in path
