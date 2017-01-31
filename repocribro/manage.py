import flask_script
import flask_migrate
from .repocribro import create_app

if __name__ == '__main__':
    app = create_app()

    manager = flask_script.Manager(app)
    manager.add_command('db', flask_migrate.MigrateCommand)
    manager.run()
