import flask
import flask_ini
import flask_injector
import flask_sqlalchemy
import injector
import os

from .extending import ExtensionsMaster
from .github import GitHubAPI

#: Paths to default configuration files
DEFAULT_CONFIG_FILES = [
    'config/app.cfg',
    'config/auth.cfg',
    'config/db.cfg'
]

#: Author of the application
AUTHOR = 'Marek Suchánek'
#: Name of the application
PROG_NAME = 'repocribro'
#: Actual release tag
RELEASE = '0.1-alpha'
#: Actual version
VERSION = '0.1'


def make_githup_api(cfg):
    """Simple factory for making the GitHub API client

    :param cfg: Configuration of the application
    :type cfg: ``configparser.ConfigParser``
    :return: GitHub API client
    :rtype: ``repocribro.github.GitHubAPI``
    """
    return GitHubAPI(
        cfg.get('github', 'client_id'),
        cfg.get('github', 'client_secret'),
        cfg.get('github', 'webhooks_secret')
    )


def create_app(cfg_files='DEFAULT'):
    """Factory for making the web Flask application

    :param cfg_files: Single or more config file(s)
    :return: Constructed web application
    :rtype: ``flask.Flask``
    """
    if cfg_files == 'DEFAULT':
        cfg_files = os.environ.get('REPOCRIBRO_CONFIG_FILE',
                                   DEFAULT_CONFIG_FILES)

    app = flask.Flask(__name__)
    app.config['RELEASE'] = RELEASE
    with app.app_context():
        app.iniconfig = flask_ini.FlaskIni()
        app.iniconfig.read(cfg_files)
    app.secret_key = app.iniconfig.get('flask', 'secret_key')

    from .database import db
    db.init_app(app)

    ext_master = ExtensionsMaster(app=app, db=db)
    ext_names = ext_master.call('introduce', 'unknown')
    print('Loaded extensions: {}'.format(', '.join(ext_names)))

    ext_master.call('init_first')
    ext_master.call('init_models')
    ext_master.call('init_business')
    ext_master.call('init_filters')
    ext_master.call('init_blueprints')

    def configure(binder):
        # TODO: let extensions make injector binds
        binder.bind(ExtensionsMaster,
                    to=ext_master,
                    scope=injector.singleton)
        binder.bind(flask_sqlalchemy.SQLAlchemy,
                    to=db,
                    scope=injector.singleton)
        binder.bind(flask_ini.FlaskIni,
                    to=app.iniconfig,
                    scope=injector.singleton)
        binder.bind(GitHubAPI,
                    to=make_githup_api(app.iniconfig),
                    scope=injector.singleton)

    inj = injector.Injector([configure])
    flask_injector.FlaskInjector(app=app, injector=inj)

    ext_master.call('init_post_injector')

    return app
