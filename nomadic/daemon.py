import click
from nomadic import nomadic, demon, conf


@click.command()
def daemon():
    """
    Launch the Nomadic daemon.
    """
    demon.start(nomadic, conf.PORT)
