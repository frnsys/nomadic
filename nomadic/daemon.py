import click

from nomadic import nomadic, demon, conf


@click.command()
@click.option('--debug', is_flag=True, help='Run in the foreground for debugging.')
def daemon(debug):
    """
    Launch the Nomadic daemon.
    """
    nomadic.index.update()

    demon.start(nomadic, conf.PORT, debug=debug)
