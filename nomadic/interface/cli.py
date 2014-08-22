import os

import click
from click import echo
from colorama import Fore, Back, Style

from nomadic import indexer, builder, searcher
from nomadic.conf import config

class Nomadic():
    def get_notebook(self, notebook):
        """
        Searches for a notebook by name
        and returns its path.

        If multiple matching notebooks were found,
        the user is promped to choose one.
        """
        if not notebook:
            notebook_dir = self.notes_path

        else:
            dirs = [nb.path for nb in self.index.notebooks if notebook in nb.name]

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
pass_nomadic = click.make_pass_decorator(Nomadic, ensure=True)

@click.group()
@pass_nomadic
def cli(nomadic):
    nomadic.index = indexer.Index(config['notes_path'])
    nomadic.builder = builder.Builder(config['notes_path'])

    for key, val in config.items():
        setattr(nomadic, key, val)

@cli.command()
@click.argument('query')
@pass_nomadic
def search(nomadic, query):
    """
    Search through notes.
    """

    # Map notes to their temporary ids.
    note_map = {}

    for idx, (result, highlights) in enumerate(searcher.search(query, nomadic.index)):
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
@pass_nomadic
def browse(nomadic, notebook):
    """
    Browse through notes
    via a web browser.
    """
    path = nomadic.get_notebook(notebook)
    if path is None: return

    path = nomadic.builder.build_path_for_path(path)
    click.launch(os.path.join(path, 'index.html'))


@cli.command()
@click.option('--reset', is_flag=True, help='Recompile the index from scratch.')
@pass_nomadic
def index(nomadic, reset):
    """
    Update or reset the note index.
    """
    if reset:
        nomadic.index.reset()
    else:
        nomadic.index.update()


@cli.command()
@pass_nomadic
def build(nomadic):
    """
    Re-build the browsable tree.
    """
    nomadic.builder.build()

@cli.command()
@pass_nomadic
def count(nomadic):
    """
    Get the number of notes.
    """
    echo('You have ' + Fore.RED + str(nomadic.index.size) + Fore.RESET + ' notes.')


@cli.command()
@click.option('-N', 'notebook', default='', help='The notebook to create the note in.')
@click.argument('note')
@pass_nomadic
def new(nomadic, notebook, note):
    """
    Create a new note.
    """
    notebook_path = nomadic.get_notebook(notebook)
    if notebook_path is None: return

    # Assume Markdown if no ext specified.
    _, ext = os.path.splitext(note)
    if not ext: note += '.md'

    path = os.path.join(notebook_path, note)
    click.edit(filename=path)
