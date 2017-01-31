import flask_script
import flask_migrate

from .repocribro import create_app


def run():
    manager = flask_script.Manager(create_app)
    manager.add_option('-c', '--config', dest='cfg_files',
                       required=False, action='append')

    manager.add_command('db', flask_migrate.MigrateCommand)

    manager.run()

if __name__ == '__main__':
    run()
