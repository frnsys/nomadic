import os
import click
from click import echo
from functools import partial
from colorama import Fore, Back
from nomadic import conf, nomadic
from nomadic.core import Note
from nomadic.util.compile import compile_note
from nomadic.util.watch import watch_note


@click.group()
def cli():
    pass


@cli.command()
@click.argument('query')
def search(query):
    """search through notes"""
    results = []

    for idx, (note, highlights) in enumerate(nomadic.search(query, delimiters=(Fore.RED, Fore.RESET))):
        path = note.path.rel
        results.append(path)

        # Show all the results.
        header = ('['+Fore.GREEN+'{0}'+Fore.RESET+'] ').format(idx)
        echo('\n' + header + Fore.BLUE + path + Fore.RESET)
        for highlight in highlights:
            echo(highlight)
        echo('\n---')

    if len(results) > 0:
        # Ask for an id and open the
        # file in the default editor.
        id = click.prompt('Select a note', type=int)
        path = results[id]
        if os.path.splitext(path)[1] == '.pdf':
            click.launch(path)
        else:
            click.edit(filename=os.path.join(conf.ROOT, path))
    else:
        echo('\nNo results for ' + Fore.RED + query + Fore.RESET + '\n')


@cli.command()
@click.argument('notebook', default='')
def browse(notebook):
    """browse notes via the web interface"""
    nb = select_notebook(notebook)
    click.launch('http://localhost:{0}/{1}/'.format(conf.PORT, nb.path.rel))


@cli.command()
@click.argument('notebook')
@click.option('--execute', is_flag=True, help='Execute the clean command')
def clean(notebook, execute):
    """remove unreferenced asset folders from a notebook,
    and clean up its notes' unreferenced assets;
    does not delete unless `--execute` is specified"""
    nb = select_notebook(notebook)
    nb.clean_assets(delete=execute)


@cli.command()
@click.argument('note')
@click.option('--rich', is_flag=True, help='Create a new "rich" (wysiwyg html) note in a browser editor')
def new(notebook, note, rich):
    """create a new note"""
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
        click.launch('http://localhost:{0}/new'.format(conf.PORT))


@cli.command()
@click.argument('note')
@click.argument('outdir')
@click.option('--watch', is_flag=True, help='watch the note for changes')
@click.option('--presentation', is_flag=True, help='compile as a presentation')
def compile(note, outdir, watch, presentation):
    """compile a note to html"""
    n = Note(note)
    if presentation:
        f = partial(compile_note, outdir=outdir, templ='presentation')
    else:
        f = partial(compile_note, outdir=outdir, templ='compiled')
    watch_note(n, f) if watch else f(n)


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
