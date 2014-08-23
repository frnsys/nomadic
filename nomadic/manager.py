"""
Manager
=======================

Management of notes and notebooks,
handles file system interaction.
"""

import os
import shutil

def note_resources(path, create=False):
    notebook, filename = os.path.split(path)
    title, ext = os.path.splitext(filename)
    resources = os.path.join(notebook, '_resources', title, '')

    if create and not os.path.exists(resources):
        os.makedirs(resources)

    return resources

def move_note(src, dest):
    from_resources = note_resources(src)
    to_resources = note_resources(dest)

    if os.path.exists(src):
        shutil.move(src, dest)

    if os.path.exists(from_resources):
        shutil.move(from_resources, to_resources)

def delete_note(path):
    """
    Delete a note and its resources
    from the filesystem.
    """
    if os.path.exists(path):
        os.remove(path)

    resources = note_resources(path)
    if os.path.exists(resources):
        shutil.rmtree(resources)

def clean_note_resources(path):
    """
    Delete resources which are not
    referenced by the note.
    """
    r = note_resources(path)
    if os.path.exists(r):
        with open(path, 'r') as note:
            content = note.read().decode('utf-8')
            for name in os.listdir(r):
                p = os.path.join(r, name)
                if os.path.isfile(p) and name not in content:
                    os.remove(p)

def save_note(path, content):
    with open(path, 'w') as note:
        note.write(content.encode('utf-8'))

def walk(path):
    """
    Walk a notes directory,
    yielding only for valid directories.
    """
    for root, dirs, files in os.walk(path):
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
    if '.SyncArchive' in path: return False
    return True

def valid_note(path):
    """
    Only certain filetypes qualify as notes,
    and we want to ignore ones named 'index.html'
    since they may be build indexes.
    """
    return path.endswith(('.html', '.md', '.pdf', '.txt')) and 'index.html' not in path
