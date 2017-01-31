import flask_script
import flask_migrate

from .commands import RepocheckCommand
from .repocribro import create_app, PROG_NAME, VERSION


def run():
    manager = flask_script.Manager(create_app)
    manager.add_option('-c', '--config', dest='cfg_files',
                       required=False, action='append',
                       default='DEFAULT')
    manager.add_option('-v', '--version', action='version',
                       version='{} v{}'.format(PROG_NAME, VERSION))

    manager.add_command('db', flask_migrate.MigrateCommand)
    manager.add_command('repocheck', RepocheckCommand)

    # TODO: allow extension add options & commands
    manager.run()

if __name__ == '__main__':
    run()
