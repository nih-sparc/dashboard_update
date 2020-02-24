import click
import sparc_dash
from blackfynn import Blackfynn

bf = Blackfynn('sparc-consortium')
ds = bf.get_dataset('SPARC Datasets')

@click.group()
def cli():
    pass

@click.command()
def clear():
    out = sparc_dash.clearRecords(ds)


@click.command()
def create_models():
    """Example script."""
    out = sparc_dash.create_models(ds)

@click.command()
def update():
    """Example script."""
    out = sparc_dash.update(bf, ds)

cli.add_command(clear)
cli.add_command(create_models)
cli.add_command(update)