import click
import flask.cli


@click.command()
@flask.cli.with_appcontext
def db_create():
    """Perform procedure create all tables"""
    db = flask.current_app.container.get('db')
    print('Performing db.create_all()')
    db.create_all()
    print('Database has been created')
