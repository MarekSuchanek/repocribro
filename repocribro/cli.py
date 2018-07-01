import click
import flask.cli

from .repocribro import create_app, PROG_NAME, VERSION


@click.group(cls=flask.cli.FlaskGroup, create_app=create_app)
def cli():
    """Repocribro CLI management"""
    # manager = flask_script.Manager(create_app)
    # manager.add_option('-c', '--config', dest='cfg_files',
    #                    required=False, action='append',
    #                    default=['DEFAULT'])
    # manager.add_option('-v', '--version', action='version',
    #                    version='{} v{}'.format(PROG_NAME, VERSION))
    #
    # manager.add_command('db', flask_migrate.MigrateCommand)
    # manager.add_command('db-create', DbCreateCommand)
    # manager.add_command('repocheck', RepocheckCommand)
    # manager.add_command('assign-role', AssignRoleCommand)
    # manager.add_command('check-config', CheckConfigCommand)
    #
    # manager.run()
    pass

if __name__ == '__main__':
    cli()
