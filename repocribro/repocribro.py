import flask
import flask_ini
import os

from .extending import ExtensionsMaster

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
RELEASE = '0.1'
#: Actual version
VERSION = '0.1'


class DI_Container:
    """Simple container of services for web app

    :ivar factories: Factories of services
    :ivar singletons: Singletons (shared objects) of services
    """

    def __init__(self):
        """Prepare dict for storing services and factories"""
        self.factories = {}
        self.singletons = {}

    def get(self, what, *args, **kwargs):
        """Retrieve service from the container

        :param what: Name of the service to get
        :type what: str
        :param args: Positional arguments passed to factory
        :param kwargs: Keyword arguments passed to factory
        :return: The service or None
        """
        if what in self.singletons:
            return self.singletons[what]
        factory = self.factories.get(what, None)
        return factory(*args, **kwargs) if callable(factory) else factory

    def set_singleton(self, name, singleton):
        """Set service as singleton (shared object)

        :param name: Name of the service
        :type name: str
        :param singleton: The object to be shared as singleton
        :type singleton: object
        """
        self.singletons[name] = singleton

    def set_factory(self, name, factory):
        """Set service factory (callable for creating instances)

        :param name: Name of the service
        :type name: str
        :param factory: Function or callable object creating service instance
        :type factory: callable
        """
        self.factories[name] = factory


class Repocribro(flask.Flask):
    """Repocribro is Flask web application

    :ivar container: Service container for the app
    :type container: ``repocribro.repocribro.DI_Container``
    """

    def __init__(self):
        """Setup Flask app and prepare service container"""
        super().__init__(PROG_NAME)
        self.container = DI_Container()


def create_app(cfg_files='DEFAULT'):
    """Factory for making the web Flask application

    :param cfg_files: Single or more config file(s)
    :return: Constructed web application
    :rtype: ``repocribro.repocribro.Repocribro``
    """
    if cfg_files == 'DEFAULT':
        cfg_files = os.environ.get('REPOCRIBRO_CONFIG_FILE',
                                   DEFAULT_CONFIG_FILES)

    app = Repocribro()
    app.config['RELEASE'] = RELEASE
    with app.app_context():
        app.iniconfig = flask_ini.FlaskIni()
        app.iniconfig.read(cfg_files)
    app.secret_key = app.iniconfig.get('flask', 'secret_key')
    app.container.set_singleton('config', app.iniconfig)

    from .database import db
    db.init_app(app)
    app.container.set_singleton('db', db)

    ext_master = ExtensionsMaster(app=app, db=db)
    ext_names = ext_master.call('introduce', 'unknown')
    print('Loaded extensions: {}'.format(', '.join(ext_names)))
    app.container.set_singleton('ext_master', ext_master)

    ext_master.call('init_first')
    ext_master.call('init_models')
    ext_master.call('init_business')
    ext_master.call('init_filters')
    ext_master.call('init_blueprints')
    ext_master.call('init_container')

    return app
