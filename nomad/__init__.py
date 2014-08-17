import os
import json

import click
from click import echo
from colorama import Fore, Back, Style

from nomad import indexer, builder, searcher, demon

class Nomad():
    pass
pass_nomad = click.make_pass_decorator(Nomad, ensure=True)

@click.group()
@pass_nomad
def cli(nomad):
    cfg = _load_config()

    nomad.index = indexer.Index(cfg['notes_dir'])
    nomad.builder = builder.Builder(cfg['notes_dir'])

    for key, val in cfg.items():
        setattr(nomad, key, val)

@cli.command()
@click.argument('query')
@pass_nomad
def search(nomad, query):
    """
    Search through notes.
    """

    # Map notes to their temporary ids.
    note_map = {}

    for idx, (result, highlights) in enumerate(searcher.search(query, nomad.index)):
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
@pass_nomad
def browse(nomad, notebook):
    """
    Browse through notes
    via a web browser.
    """
    if not notebook:
        notebook_dir = nomad.notes_dir

    else:
        dirs = []
        for root, dirnames, _ in indexer.walk_notes(nomad.notes_dir):
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

    path = notebook_dir.replace(nomad.notes_dir, nomad.build_dir)
    click.launch(os.path.join(path, 'index.html'))


@cli.command()
@click.option('--reset', is_flag=True, help='Recompile the index from scratch.')
@pass_nomad
def index(nomad, reset):
    """
    Manually update or reset the note index.
    """
    if reset:
        nomad.index.reset()
    else:
        nomad.index.update()


@cli.command()
@pass_nomad
def build(nomad):
    """
    Manually re-build the browsable tree.
    """
    nomad.builder.build()




@click.command()
@click.option('--debug', is_flag=True, help='Run in the foreground for debugging.')
def daemon(debug):
    """
    Launch the Nomad daemon.
    """
    cfg = _load_config()
    demon.start(cfg['notes_dir'], debug=debug)





def _load_config():
    cfg_path = os.path.expanduser(u'~/.nomad')

    # Create default config if necessary.
    if not os.path.exists(cfg_path):
        with open(cfg_path, 'w') as cfg_file:
            json.dump(cfg_file, {
                'notes_dir': '~/nomad'
            })

    with open(cfg_path, 'r') as cfg_file:
        cfg = json.load(cfg_file)

    cfg['notes_dir'] = os.path.expanduser(cfg['notes_dir'])
    cfg['build_dir'] = os.path.join(cfg['notes_dir'], u'.build')
    return cfg

def _echo_path_choice(idx, path):
    """
    Echo multiple numbered path choices.
    """
    header = ('\n'+'['+Fore.GREEN+'{0}'+Fore.RESET+'] ').format(idx)
    echo(Back.BLACK + header + Fore.YELLOW + path + Style.RESET_ALL)
