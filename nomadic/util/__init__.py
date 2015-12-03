import os

def valid_notebook(path):
    """
    We want to ignore the build and all resource directories.
    """
    if not os.path.isdir(path):
        return False

    # Ignore hidden directories and directories starting with '_'
    if path.strip('/').split('/')[-1][0] in ['.', '_']:
        return False

    for excluded in ['_resources', 'assets', '.SyncArchive', '.SyncID', '.SyncIgnore', '.sync', '.DS_Store', '.swp', '.swo', '.stfolder', '.git']:
        if excluded in path: return False
    return True


def valid_note(path):
    """
    Only certain filetypes qualify as notes.
    """
    return path.endswith(('.md', '.txt', '.pdf'))
