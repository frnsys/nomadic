import click

from nomadic.core import Nomadic
from nomadic import demon, conf


@click.command()
@click.option('--debug', is_flag=True, help='Run in the foreground for debugging.')
def daemon(debug):
    """
    Launch the Nomadic daemon.
    """

    nomadic = Nomadic(conf.ROOT)
    nomadic.index.update()
    nomadic.builder.build()

    demon.start(nomadic, conf.PORT, debug=debug)
