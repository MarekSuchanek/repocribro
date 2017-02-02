from .extending import Extension
from .extending.helpers import ExtensionView
import flask_bower
import flask_migrate


class CoreExtension(Extension):
    NAME = 'core'
    CATEGORY = 'basic'
    AUTHOR = 'Marek Suchánek'
    GH_URL = 'https://github.com/MarekSuchanek/repocribro'

    def __init__(self, app, db, *args, **kwargs):
        super().__init__(app, db)
        self.bower = flask_bower.Bower(self.app)
        self.migrate = flask_migrate.Migrate(self.app, self.db)

    @staticmethod
    def provide_models():
        from .models import all_models
        return all_models

    @staticmethod
    def provide_blueprints():
        from .controllers import all_blueprints
        return all_blueprints

    @staticmethod
    def provide_filters():
        from .filters import all_filters
        return all_filters

    def init_business(self, *args, **kwargs):
        from .security import init_login_manager
        login_manager, principals = init_login_manager(self.db)
        login_manager.init_app(self.app)
        principals.init_app(self.app)

    def init_post_injector(self, *args, **kwargs):
        # flask_restless is not compatible with flask_injector!
        from .api import create_api
        api_manager = create_api(self.app, self.db)


def make_extension(*args, **kwargs):
    return CoreExtension(*args, **kwargs)
