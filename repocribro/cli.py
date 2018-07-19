import click
import flask.cli

from .repocribro import create_app


@click.group(cls=flask.cli.FlaskGroup, create_app=create_app)
def cli():
    """Repocribro CLI management"""
    pass


if __name__ == '__main__':
    cli()
