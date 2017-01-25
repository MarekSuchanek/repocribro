import flask
import flask_bower
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import configparser
from .models import db
import os

basedir = os.path.abspath(os.path.dirname(__file__))


# TODO: app factory and/or subclass
def create_app():
    app = flask.Flask(__name__)
    flask_bower.Bower(app)

    # TODO: db config file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///repocribro_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)

    from .security import login_manager, principals
    login_manager.init_app(app)
    principals.init_app(app)

    from .api import create_api
    api_manager = create_api(app)
    # TODO: load all parts
    # TODO: load all extensions

    cfg = configparser.ConfigParser()
    cfg.read('config/auth.cfg')

    # TODO: load config file(s), make config class (defaults)
    app.config['DEBUG'] = True # TODO: from config
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['GH_BASIC_CLIENT_ID'] = cfg['github']['client_id']
    app.config['GH_BASIC_CLIENT_SECRET'] = cfg['github']['client_secret']
    app.secret_key = cfg['flask']['secret_key']

    init_controllers(app)
    return app


def init_controllers(app):
    from .controllers import auth, core, errors, user, webhooks
    app.register_blueprint(auth)
    app.register_blueprint(core)
    app.register_blueprint(errors)
    app.register_blueprint(user)
    app.register_blueprint(webhooks)


app = create_app()

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


def start():
    app.run()
