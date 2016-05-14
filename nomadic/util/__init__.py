import os


def valid_notebook(path):
    """we want to ignore the build and all resource directories"""
    if not os.path.isdir(path):
        return False

    # ignore hidden directories and directories starting with '_'
    if path.strip('/').split('/')[-1][0] in ['.', '_']:
        return False

    excluded = ['_resources', 'assets', '.SyncArchive', '.SyncID', '.SyncIgnore',
                '.sync', '.DS_Store', '.swp', '.swo', '.stfolder', '.git']
    return not any(ex in path for ex in excluded)


def valid_note(path):
    """only certain filetypes qualify as notes"""
    return path.endswith(('.md', '.txt', '.pdf'))
