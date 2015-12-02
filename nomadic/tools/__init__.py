import click
from nomadic.core.models import Note
from nomadic.tools import presentation


@click.group()
def tools():
    pass


@tools.command()
@click.argument('note')
@click.argument('outdir')
def export_presentation(note, outdir):
    """
    Export a note as a portable presentation.
    """
    n = Note(note)
    presentation.compile_presentation(n, outdir)


@tools.command()
@click.argument('note')
@click.argument('outdir')
def watch_presentation(note, outdir):
    """
    Watches a presentation note and its assets directory
    and exports an updated version on changes.
    """
    n = Note(note)
    presentation.watch_presentation(n, outdir)
