import click

from nomadic import indexer, builder, demon
from nomadic.conf import config

@click.command()
@click.option('--debug', is_flag=True, help='Run in the foreground for debugging.')
def daemon(debug):
    """
    Launch the Nomadic daemon.
    """
    notes_path = config['notes_path']

    # Update the index.
    indexer.Index(notes_path).update()

    # Build the browsable tree.
    builder.Builder(notes_path).build()

    # Start the daemon.
    demon.start(notes_path, config['port'], debug=debug)
