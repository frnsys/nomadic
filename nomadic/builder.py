"""
Builder
=======================

Builds note files a local HTML site.
"""

import os
import shutil
from collections import namedtuple

import lxml.html
from lxml.etree import tostring
from markdown import markdown
from jinja2 import Template, FileSystemLoader, environment

File = namedtuple('File', ['title', 'filename'])

# Load templates.
path = os.path.abspath(__file__)
dir = os.path.dirname(path)

env = environment.Environment()
env.loader = FileSystemLoader(os.path.join(dir, 'templates'))
index_templ = env.get_template('notebook.html')
md_templ = env.get_template('markdown.html')

class Builder():
    def __init__(self, notes_path):
        # The last '' is to ensure a trailing slash.
        self.notes_path = os.path.join(notes_path, '')
        self.build_path = os.path.join(notes_path, u'.build', '')

        self._prepare_build_dir()


    def _prepare_build_dir(self, reset=False):
        """
        Prepare the build directory,
        creating it if necessary.
        """
        if reset and os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)

        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)

    def build(self):
        """
        Compile all notes into a
        browsable HTML structure.
        """
        self._prepare_build_dir(reset=True)
        self.compile_notebook(self.notes_path)

    def compile_notebook(self, path):
        """
        Build a notebook, recursively,
        compiling notes and indexes.
        """
        for root, dirnames, filenames in os.walk(path):
            if _valid_notebook(root):
                build_root = root.replace(self.notes_path, self.build_path)

                dirs = []
                files = []

                # Process valid sub-directories.
                for dirname in dirnames:
                    if _valid_notebook(dirname):
                        build_path = os.path.join(build_root, dirname)

                        if os.path.exists(build_path):
                            shutil.rmtree(build_path)
                        os.makedirs(build_path)

                        dirs.append(dirname.decode('utf-8'))

                # Process notes.
                for filename in filenames:
                    if filename == 'index.html':
                        continue
                    title, ext = os.path.splitext(filename)
                    compiled_filename = title + '.html'
                    if ext in ['.html', '.md']:
                        path = os.path.join(root, filename)

                        self.compile_note(path)

                        file = File(title, compiled_filename)
                        files.append(file)

                # Write the index file for this node.
                self._write_index(build_root, dirs, files)

    def compile_note(self, path):
        """
        Compile a single Markdown or
        HTML note to the build tree.

        This will overwrite the
        existing note, if any.
        """
        build_path, ext = self.build_path_for_note_path(path)
        crumbs = self._build_breadcrumbs(build_path)

        # Process all relative paths to
        # point to the raw note directories,
        # so we don't have to copy resources over.
        with open(path, 'rb') as note:
            content = ''
            raw_content = note.read().decode('utf-8')
            if ext == '.html':
                raw_html = raw_content
            else:
                rendered = markdown(raw_content)
                raw_html = md_templ.render(html=rendered, crumbs=crumbs)

            if raw_html:
                html = lxml.html.fromstring(raw_html)
                html.rewrite_links(_rewrite_link, base_href=build_path)
                content = tostring(html, method='html')

            # Write the compiled note.
            with open(build_path, 'w') as build_note:
                build_note.write(content.encode('utf-8'))


    def delete_note(self, path):
        """
        Deletes a compiled note
        from the build tree.
        """
        build_path, _ = self.build_path_for_note_path(path)

        if os.path.exists(build_path):
            os.remove(build_path)

    def delete_notebook(self, path):
        """
        Deletes a compiled notebook
        from the build tree.
        """
        build_path = self.build_path_for_path(path)

        if os.path.exists(build_path):
            shutil.rmtree(build_path)

    def index_notebook(self, dir):
        """
        Compiles an index for a given directory.
        This does not compile the notes in the directory,
        nor is it recursive.
        """
        dirs = []
        files = []
        build_path = self.build_path_for_path(dir)
        for name in os.listdir(dir):
            path = os.path.join(dir, name)
            if os.path.isfile(path):
                title, ext = os.path.splitext(name)
                if ext in ['.html', '.md']:
                    compiled_filename = title + '.html'
                    file = File(title.decode('utf-8'), compiled_filename.decode('utf-8'))
                    files.append(file)
            else:
                if _valid_notebook(name):
                    dirs.append(name.decode('utf-8'))
        # Write the index file for this node.
        self._write_index(build_path, dirs, files)


    def build_path_for_note_path(self, path):
        """
        Returns a compiled note path for a given
        regular note path.

        Also returns the original extension.

        Notes are compiled to html so
        the extension will be `.html`.
        """
        build_path = self.build_path_for_path(path)
        base, ext = os.path.splitext(build_path)
        return base + '.html', ext

    def build_path_for_path(self, path):
        """
        Returns a build path
        for a given path.
        """
        if '.build' not in path:
            path = self.normalize_path(path)
            path = path.replace(self.notes_path, self.build_path)
        return path

    def normalize_path(self, path):
        """
        Normalizes a directory path
        so that it has a trailing slash and
        groups of slashes are compressed.
        
        i.e. 'A///B' => 'A/B/'
        """
        path = os.path.normpath(path)
        if os.path.isdir(path):
            path = os.path.join(path, '')
        return path

    def _write_index(self, path, dirs, files):
        """
        Write an `index.html` file
        at the specified path,
        listing the specified dirs and files.
        """
        crumbs = self._build_breadcrumbs(path)
        rendered = index_templ.render(dirs=dirs, files=files, crumbs=crumbs)

        if not os.path.exists(path):
            os.makedirs(path)

        with open( os.path.join(path, 'index.html'), 'w' ) as index:
            index.write(rendered.encode('utf-8'))

    def _build_breadcrumbs(self, path):
        # Get rid of the build path.
        path = path.replace(self.build_path, '')

        # Create some name for the root notebook.
        path = os.path.join('notes', path)

        # Split the path into the crumbs.
        # Filter out any empty crumbs.
        crumbs = filter(None, path.split('/'))

        # Remove the file extension from the last crumb.
        crumbs[-1], _ = os.path.splitext(crumbs[-1])

        return crumbs


def _rewrite_link(link):
    root, ext = os.path.splitext(link)
    if ext not in ['.html', '.md']:
        return link.replace('.build/', '')
    elif ext == '.md':
        return root + '.html'
    return link


def _valid_notebook(dir):
    """
    We want to ignore the build and searchindex
    as well as all resource directories.
    """
    if '.build' in dir: return False
    if '.searchindex' in dir: return False
    if '_resources' in dir: return False
    return True
