import flask
import flask_injector
import flask_sqlalchemy
import injector
import configparser
from .extending import ExtensionsMaster
from .github import GitHubAPI


def create_app(cfg):
    app = flask.Flask(__name__)

    # TODO: db config file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///repocribro_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # TODO: load config file(s), make config class (defaults)
    app.config['DEBUG'] = True  # TODO: from config
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['GH_BASIC_CLIENT_ID'] = cfg['github']['client_id']
    app.config['GH_BASIC_CLIENT_SECRET'] = cfg['github']['client_secret']
    app.config['GH_BASIC_WEBHOOKS_SECRET'] = cfg['github']['webhooks_secret']
    app.secret_key = cfg['flask']['secret_key']

    from .models import db
    db.init_app(app)

    ext_master = ExtensionsMaster(app=app, db=db)
    ext_names = ext_master.call('introduce', 'unknown')
    print('Loaded extensions: {}'.format(', '.join(ext_names)))

    ext_master.call('init_first')
    ext_master.call('init_business')
    ext_master.call('init_filters')
    ext_master.call('init_blueprints')

    def configure(binder):
        # TODO: let extensions make injector binds
        binder.bind(ExtensionsMaster,
                    to=ext_master, scope=injector.singleton)
        binder.bind(flask_sqlalchemy.SQLAlchemy,
                    to=db, scope=injector.singleton)
        binder.bind(GitHubAPI,
                    to=GitHubAPI(), scope=injector.singleton)

    inj = injector.Injector([configure])
    flask_injector.FlaskInjector(app=app, injector=inj)

    ext_master.call('init_post_injector')

    return app


def get_auth_cfg(cfg_file='config/auth.cfg'):
    auth_cfg = configparser.ConfigParser()
    auth_cfg.read(cfg_file)
    return auth_cfg


def start():
    auth_cfg = get_auth_cfg()
    app = create_app(auth_cfg)
    app.run()
