import os
import click
from click import echo
from functools import partial
from colorama import Fore, Back
from nomadic import conf, nomadic
from nomadic.core import Note
from nomadic.util import html2md, parsers, clipboard, compile
from nomadic.util.watch import watch_note


@click.group()
def cli():
    pass


@cli.command()
@click.argument('query')
@click.option('-b', '--browser', is_flag=True, help='open with browser, only for non-pdfs')
@click.option('-p', '--include-pdf', is_flag=True, help='include pdfs in search (slower)')
def search(query, browser, include_pdf):
    """search through notes"""
    results = []

    for idx, (note, highlights) in enumerate(nomadic.search(query,
                                                            delimiters=(Fore.RED, Fore.RESET),
                                                            include_pdf=include_pdf)):
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
        abs_path = os.path.join(conf.ROOT, path)
        if os.path.splitext(path)[1] == '.pdf':
            click.launch(abs_path)
        else:
            if not browser:
                click.edit(filename=abs_path)
            else:
                click.launch('http://localhost:{0}/{1}'.format(conf.PORT, path))
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
@click.option('-x', '--execute', is_flag=True, help='execute the clean command')
def clean(notebook, execute):
    """remove unreferenced asset folders from a notebook,
    and clean up its notes' unreferenced assets;
    does not delete unless `--execute` is specified"""
    nb = select_notebook(notebook)
    nb.clean_assets(delete=execute)


@cli.command()
@click.argument('note')
def new(notebook, note):
    """create a new note"""
    nb = select_notebook(notebook)
    if nb is None:
        echo('The notebook `{0}` doesn\'t exist.'.format(notebook))
        return

    # Assume Markdown if no ext specified.
    _, ext = os.path.splitext(note)
    if not ext: note += '.md'

    path = os.path.join(nb.path.abs, note)
    click.edit(filename=path)


@cli.command()
@click.argument('note')
def view(note):
    """view a note in the browser, recompiling when changed"""
    # convert to abs path; don't assume we're in the notes folder
    outdir = '/tmp'
    note = os.path.join(os.getcwd(), note)
    n = Note(note)
    compile.compile_note(n, outdir=outdir, templ='default')
    click.launch('/tmp/{title}/{title}.html'.format(title=n.title))
    f = partial(compile.compile_note, outdir=outdir, templ='default')
    watch_note(n, f)


@cli.command()
@click.argument('note')
@click.argument('outdir')
@click.option('-w', '--watch', is_flag=True, help='watch the note for changes')
def export(note, outdir, watch):
    """export a note to html"""
    # convert to abs path; don't assume we're in the notes folder
    note = os.path.join(os.getcwd(), note)
    n = Note(note)
    f = partial(compile.compile_note, outdir=outdir, templ='default')
    watch_note(n, f) if watch else f(n)


@cli.command()
@click.option('-s', '--save', help='note path to save to. will download images')
@click.option('-e', '--edit', is_flag=True, help='edit the note after saving')
@click.option('-b', '--browser', is_flag=True, help='open the note in the browser after saving')
@click.option('-o', '--overwrite', is_flag=True, help='overwrite existing note')
def clip(save, edit, browser, overwrite):
    """convert html in the clipboard to markdown"""
    html = clipboard.get_clipboard_html()
    if html is None:
        click.echo('No html in the clipboard')
        return

    if save is None:
        content = html2md.html_to_markdown(html).strip()
        click.echo(content)
        return

    if not save.endswith('.md'):
        click.echo('Note must have extension ".md"')
        return

    note = Note(save)
    if os.path.exists(note.path.abs) and not overwrite:
        click.echo('Note already exists at "{}" (specify `--overwrite` to overwrite)'.format(note.path.abs))
        return

    html = parsers.rewrite_external_images(html, note)
    content = html2md.html_to_markdown(html).strip()
    note.write(content)

    if browser:
        click.launch('http://localhost:{0}/{1}'.format(conf.PORT, note.path.rel))

    if edit:
        click.edit(filename=note.path.abs)


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
