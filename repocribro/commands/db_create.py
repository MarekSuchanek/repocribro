import click
import flask.cli


def _db_create():
    db = flask.current_app.container.get('db')
    print('Performing db.create_all()')
    db.create_all()
    print('Database has been created')


@click.command()
@flask.cli.with_appcontext
def db_create():
    """Perform procedure create all tables"""
    _db_create()
