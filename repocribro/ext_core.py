from .extending import Extension
from .extending.helpers import ExtensionView
import flask_bower
import flask_migrate


# TODO: some methods can be generic or simplified
class CoreExtension(Extension):
    NAME = 'core'
    CATEGORY = 'basic'
    AUTHOR = 'Marek Suchánek'
    GH_URL = 'https://github.com/MarekSuchanek/repocribro'

    def __init__(self, app, db, *args, **kwargs):
        self.app = app
        self.db = db
        self.bower = flask_bower.Bower(self.app)
        self.migrate = flask_migrate.Migrate(self.app, self.db)

    def call(self, hook_name, default, *args, **kwargs):
        operation = getattr(self, hook_name, None)
        if callable(operation):
            return operation(*args, **kwargs)
        else:
            return default

    def init_business(self, *args, **kwargs):
        from .security import init_login_manager
        login_manager, principals = init_login_manager(self.db)
        login_manager.init_app(self.app)
        principals.init_app(self.app)

    def init_models(self, *args, **kwargs):
        from .models import all_models
        return all_models

    def init_blueprints(self, *args, **kwargs):
        from .controllers import admin, auth, core, errors, manage, webhooks
        self.app.register_blueprint(admin)
        self.app.register_blueprint(auth)
        self.app.register_blueprint(core)
        self.app.register_blueprint(errors)
        self.app.register_blueprint(manage)
        self.app.register_blueprint(webhooks)

    def init_filters(self, *args, **kwargs):
        from .filters import register_filters
        register_filters(self.app)

    def init_post_injector(self, *args, **kwargs):
        # flask_restless is not compatible with flask_injector!
        from .api import create_api
        api_manager = create_api(self.app, self.db)

    def introduce(self, *args, **kwargs):
        return self.NAME

    def view_admin_extensions(self, *args, **kwargs):
        return ExtensionView(
            self.NAME,
            self.CATEGORY,
            self.AUTHOR,
            gh_url=self.GH_URL
        )


def make_extension(*args, **kwargs):
    return CoreExtension(*args, **kwargs)
