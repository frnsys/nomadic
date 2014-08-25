import click

from nomadic.core import Nomadic, demon
from nomadic.interface.conf import config

@click.command()
@click.option('--debug', is_flag=True, help='Run in the foreground for debugging.')
def daemon(debug):
    """
    Launch the Nomadic daemon.
    """
    nomadic = Nomadic(config['notes_path'])

    # Update the index.
    nomadic.index.update()

    # Build the browsable tree.
    nomadic.builder.build()

    # Start the daemon.
    demon.start(nomadic, config['port'], debug=debug)
