import os

import click
from click import echo
from colorama import Fore, Back, Style

from nomadic import conf
from nomadic.core import Nomadic
from nomadic.util import evernote

nomadic = Nomadic(conf.ROOT)

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
        header = ('['+Fore.GREEN+'{0}'+Fore.RESET+'] ').format(idx)
        echo('\n' + header + Back.BLUE + Fore.WHITE + path + Back.RESET + Fore.RESET)
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
    nb = select_notebook(notebook)

    path = nomadic.builder.to_build_path(nb.path.abs)
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
    echo('You have ' + Fore.GREEN + str(nomadic.index.size) + Fore.RESET + ' notes.')

@cli.command()
@click.argument('html_path', type=click.Path())
@click.option('-N', 'notebook', default='', help='The notebook to create the note in.')
def convert(notebook, html_path):
    """
    Convert an HTML note into a Markdown
    note and save it.
    """
    nb = select_notebook(notebook)
    if nb is None:
        echo('The notebook `{0}` doesn\'t exist.'.format(notebook))
        return

    note_path = evernote.port_evernote(html_path, nb)
    click.edit(filename=note_path)


@cli.command()
@click.option('-N', 'notebook', default='', help='The notebook to create the note in.')
@click.argument('note')
@click.option('--rich', is_flag=True, help='Create a new "rich" (wysiwyg html) note in a browser editor')
def new(notebook, note, rich):
    """
    Create a new note.
    """
    nb = select_notebook(notebook)
    if nb is None:
        echo('The notebook `{0}` doesn\'t exist.'.format(notebook))
        return

    if not rich:
        # Assume Markdown if no ext specified.
        _, ext = os.path.splitext(note)
        if not ext: note += '.md'

        path = os.path.join(nb.path.abs, note)
        click.edit(filename=path)
    else:
        # Launch the daemon server's rich editor.
        click.launch('http://localhost:{0}/new'.format(nomadic.port))


def select_notebook(name):
    if not name:
        notebook = nomadic.rootbook

    else:
        notebooks = [nb for nb in nomadic.rootbook.notebooks if name in nb.name]

        if len(notebooks) == 1:
            notebook = notebooks[0]

        elif len(notebooks) > 1:
            echo('\nFound multiple matching notebooks:\n')
            for idx, notebook in enumerate(notebooks):
                header = ('['+Fore.GREEN+'{0}'+Fore.RESET+'] ').format(idx)
                echo('\n' + header + Back.BLUE + Fore.WHITE + notebook.path.rel + Back.RESET + Fore.RESET)
            idx = click.prompt('Select a notebook', type=int)
            notebook = notebooks[idx]

        else:
            echo('\nNo matching notebooks found.\n')
            return
    return notebook
