
def valid_notebook(path):
    """
    We want to ignore the build and searchindex
    as well as all resource directories.
    """
    if '.build' in path: return False
    if '.searchindex' in path: return False
    if '_resources' in path: return False
    if '.SyncArchive' in path: return False
    return True


def valid_note(path):
    """
    Only certain filetypes qualify as notes,
    and we want to ignore ones named 'index.html'
    since they may be build indexes.
    """
    return path.endswith(('.html', '.md', '.pdf', '.txt')) and 'index.html' not in path
