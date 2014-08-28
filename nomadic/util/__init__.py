
def valid_notebook(path):
    """
    We want to ignore the build and searchindex
    as well as all resource directories.
    """
    for excluded in ['.build', '.searchindex', '_resources', '.SyncArchive']:
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
