import os

import click
from click import echo
from colorama import Fore, Back, Style

from nomadic.core import Nomadic
from nomadic.interface.conf import config

nomadic = Nomadic(config['notes_path'])

@click.group()
def cli():
    pass

@cli.command()
@click.argument('query')
def search(query):
    """
    Search through notes.
    """

    # Map notes to their temporary ids.
    note_map = {}

    for idx, (result, highlights) in enumerate(nomadic.index.search(query)):
        path = result['path']
        note_map[idx] = path

        # Show all the results.
        header = ('\n'+'['+Fore.GREEN+'{0}'+Fore.RESET+'] ').format(idx)
        echo(Back.BLACK + header + Fore.YELLOW + path + Back.RESET + Fore.RESET)
        echo(highlights)
        echo('\n---')

    if len(note_map) > 0:
        # Ask for an id and open the
        # file in the default editor.
        id = click.prompt('Select a note', type=int)
        path = note_map[id]
        if os.path.splitext(path)[1] == '.pdf':
            click.launch(path)
        else:
            click.edit(filename=path)
    else:
        echo('\nNo results for ' + Fore.RED + query + Fore.RESET + '\n')

@cli.command()
@click.argument('notebook', default='')
def browse(notebook):
    """
    Browse through notes
    via a web browser.
    """
    notebook_path = select_notebook(notebook)

    path = nomadic.builder.build_path_for_path(notebook_path)
    click.launch(os.path.join(path, 'index.html'))


@cli.command()
@click.option('--reset', is_flag=True, help='Recompile the index from scratch.')
def index(reset):
    """
    Update or reset the note index.
    """
    if reset:
        nomadic.index.reset()
    else:
        nomadic.index.update()


@cli.command()
def build():
    """
    Re-build the browsable tree.
    """
    nomadic.builder.build()

@cli.command()
def count():
    """
    Get the number of notes.
    """
    echo('You have ' + Fore.RED + str(nomadic.index.size) + Fore.RESET + ' notes.')

@cli.command()
@click.argument('html_path', type=click.Path())
@click.option('-N', 'notebook', default='', help='The notebook to create the note in.')
def convert(notebook, html_path):
    """
    Convert an HTML note into a Markdown
    note and save it.
    """
    notebook_path = select_notebook(notebook)
    if notebook_path is None:
        echo('The notebook `{0}` doesn\'t exist.'.format(notebook))
        return

    basepath, filename = os.path.split(html_path)
    title, ext = os.path.splitext(filename)

    with open(html_path, 'r') as html_file:
        html = html_file.read()

    markdown = converter.html_to_markdown(html)

    # Add in the title.
    markdown = '# {0}\n\n'.format(title) + markdown

    path = os.path.join(notebook_path, title + '.md')
    with open(path, 'w') as note:
        note.write(markdown.encode('utf-8'))


@cli.command()
@click.option('-N', 'notebook', default='', help='The notebook to create the note in.')
@click.argument('note')
@click.option('--rich', is_flag=True, help='Create a new "rich" (wysiwyg html) note in a browser editor')
def new(notebook, note, rich):
    """
    Create a new note.
    """
    notebook_path = select_notebook(notebook)
    if notebook_path is None:
        echo('The notebook `{0}` doesn\'t exist.'.format(notebook))
        return

    if not rich:
        # Assume Markdown if no ext specified.
        _, ext = os.path.splitext(note)
        if not ext: note += '.md'

        path = os.path.join(notebook_path, note)
        click.edit(filename=path)
    else:
        # Launch the daemon server's rich editor.
        click.launch('http://localhost:{0}/new'.format(nomadic.port))


def select_notebook(notebook):
    if not notebook:
        notebook_dir = nomadic.notes_path

    else:
        dirs = [nb.path for nb in nomadic.index.notebooks if notebook in nb.name]

        if len(dirs) == 1:
            notebook_dir = dirs[0]

        elif len(dirs) > 1:
            echo('\nFound multiple matching notebooks:\n')
            for idx, dir in enumerate(dirs):
                header = ('\n'+'['+Fore.GREEN+'{0}'+Fore.RESET+'] ').format(idx)
                echo(Back.BLACK + header + Fore.YELLOW + path + Back.RESET + Fore.RESET)
            idx = click.prompt('Select a notebook', type=int)
            notebook_dir = dirs[idx]

        else:
            echo('\nNo matching notebooks found.\n')
            return
    return notebook_dir
