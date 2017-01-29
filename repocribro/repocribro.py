import flask
import flask_bower
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import configparser
import os


# TODO: app factory and/or subclass
def create_app(cfg):
    app = flask.Flask(__name__)
    flask_bower.Bower(app)

    # TODO: db config file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///repocribro_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    from .models import db
    db.init_app(app)

    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    from .security import login_manager, principals
    login_manager.init_app(app)
    principals.init_app(app)

    from .api import create_api
    api_manager = create_api(app)
    # TODO: load all parts
    # TODO: load all extensions

    # TODO: load config file(s), make config class (defaults)
    app.config['DEBUG'] = True  # TODO: from config
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['GH_BASIC_CLIENT_ID'] = cfg['github']['client_id']
    app.config['GH_BASIC_CLIENT_SECRET'] = cfg['github']['client_secret']
    app.config['GH_BASIC_WEBHOOKS_SECRET'] = cfg['github']['webhooks_secret']
    app.secret_key = cfg['flask']['secret_key']

    from .filters import register_filters
    register_filters(app)

    init_controllers(app)
    return app, manager


def init_controllers(app):
    from .controllers import admin, auth, core, errors, manage, webhooks
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(core)
    app.register_blueprint(errors)
    app.register_blueprint(manage)
    app.register_blueprint(webhooks)


def get_auth_cfg(cfg_file='config/auth.cfg'):
    auth_cfg = configparser.ConfigParser()
    auth_cfg.read(cfg_file)
    return auth_cfg


def start():
    auth_cfg = get_auth_cfg()
    app, manager = create_app(auth_cfg)
    app.run()
