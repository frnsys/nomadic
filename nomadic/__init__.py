import os
import json

import click
from click import echo
from colorama import Fore, Back, Style

from nomadic import indexer, builder, searcher, demon

class Nomadic():
    pass
pass_nomadic = click.make_pass_decorator(Nomadic, ensure=True)

@click.group()
@pass_nomadic
def cli(nomadic):
    cfg = _load_config()

    nomadic.index = indexer.Index(cfg['notes_dir'])
    nomadic.builder = builder.Builder(cfg['notes_dir'])

    for key, val in cfg.items():
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
        note_map[idx] = result['path']

        # Show all the results.
        _echo_path_choice(idx, result['path'])
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
    if not notebook:
        notebook_dir = nomadic.notes_dir

    else:
        dirs = []
        for root, dirnames, _ in indexer.walk_notes(nomadic.notes_dir):
            dirs += [os.path.join(root, dirname) for dirname in dirnames if notebook in dirname]

        if len(dirs) == 1:
            notebook_dir = dirs[0]

        elif len(dirs) > 1:
            echo('\nFound multiple matching notebooks:\n')
            for idx, dir in enumerate(dirs):
                _echo_path_choice(idx, dir)
            idx = click.prompt('Select a notebook', type=int)
            notebook_dir = dirs[idx]

        else:
            echo('\nNo matching notebooks found.\n')
            return

    path = notebook_dir.replace(nomadic.notes_dir, nomadic.build_dir)
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




@click.command()
@click.option('--debug', is_flag=True, help='Run in the foreground for debugging.')
def daemon(debug):
    """
    Launch the Nomadic daemon.
    """
    cfg = _load_config()
    notes_path = cfg['notes_dir']

    # Update the index.
    indexer.Index(notes_path).update()

    # Build the browsable tree.
    builder.Builder(notes_path).build()

    # Start the daemon.
    demon.start(notes_path, debug=debug)





def _load_config():
    cfg_path = os.path.expanduser(u'~/.nomadic')

    # Create default config if necessary.
    if not os.path.exists(cfg_path):
        with open(cfg_path, 'w') as cfg_file:
            json.dump({
                'notes_dir': '~/nomadic'
            }, cfg_file)

    with open(cfg_path, 'r') as cfg_file:
        cfg = json.load(cfg_file)

    notes_path = os.path.expanduser(cfg['notes_dir'])
    cfg['notes_dir'] = notes_path
    cfg['build_dir'] = os.path.join(notes_path, u'.build')

    # Create the notes directory if necessary.
    if not os.path.exists(notes_path):
        os.makedirs(notes_path)

    return cfg

def _echo_path_choice(idx, path):
    """
    Echo multiple numbered path choices.
    """
    header = ('\n'+'['+Fore.GREEN+'{0}'+Fore.RESET+'] ').format(idx)
    echo(Back.BLACK + header + Fore.YELLOW + path + Style.RESET_ALL)
