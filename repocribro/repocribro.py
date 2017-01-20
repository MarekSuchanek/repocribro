import flask
import flask_bower
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import configparser
from .core import core
from .auth import auth
from .user import user
from .models import db
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# TODO: app factory and/or subclass
app = flask.Flask(__name__)
flask_bower.Bower(app)

# TODO: db config file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///repocribro_dev.db'
db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

app.register_blueprint(core)
app.register_blueprint(auth)
app.register_blueprint(user)
# TODO: load all parts
# TODO: load all extensions


@app.errorhandler(403)
def not_found(error):
    return flask.render_template('error/403.html'), 403


@app.errorhandler(404)
def not_found(error):
    return flask.render_template('error/404.html'), 404


@app.errorhandler(410)
def not_found(error):
    return flask.render_template('error/410.html'), 410


@app.errorhandler(500)
def not_found(error):
    return flask.render_template('error/500.html'), 500


def start():
    # TODO: improve CLI for start
    # TODO: load config file(s), make config class (defaults)
    cfg = configparser.ConfigParser()
    cfg.read('config/auth.cfg')

    app.config['DEBUG'] = True # TODO: from config
    app.config['GH_BASIC_CLIENT_ID'] = cfg['github']['client_id']
    app.config['GH_BASIC_CLIENT_SECRET'] = cfg['github']['client_secret']
    app.secret_key = cfg['flask']['secret_key']
    app.run()
