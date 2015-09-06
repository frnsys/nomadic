import os

def valid_notebook(path):
    """
    We want to ignore the build and searchindex
    as well as all resource directories.
    """
    if not os.path.isdir(path):
        return False
    for excluded in ['.searchindex', '_resources', 'assets', '.SyncArchive', '.SyncID', '.SyncIgnore', '.sync', '.DS_Store', '.swp', '.swo', '.stfolder', '.git']:
        if excluded in path: return False
    return True


def valid_note(path):
    """
    Only certain filetypes qualify as notes,
    and we want to ignore ones named 'index.html'
    since they may be build indexes.

    When indexing files, pdfs are also included.
    """
    return path.endswith(('.html', '.md', '.txt', '.pdf')) and 'index.html' not in path
