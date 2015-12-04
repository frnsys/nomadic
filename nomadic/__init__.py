import click
from nomadic import demon, conf
from nomadic.core import Nomadic

nomadic = Nomadic(conf.ROOT)


@click.command()
def daemon():
    """launch the Nomadic daemon"""
    demon.start(nomadic, conf.PORT)
