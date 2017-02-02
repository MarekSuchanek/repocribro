from .helpers import ExtensionView


def no_models():
    return []


class Extension:
    NAME = 'unknown'
    CATEGORY = ''
    AUTHOR = ''
    ADMIN_URL = None
    HOME_URL = None
    GH_URL = None

    def __init__(self, app, db, *args, **kwargs):
        self.app = app
        self.db = db

    def call(self, hook_name, default, *args, **kwargs):
        operation = getattr(self, hook_name, None)
        if callable(operation):
            return operation(*args, **kwargs)
        else:
            return default

    def register_filters_from_dict(self, filters):
        for name, func in filters.items():
            self.app.jinja_env.filters[name] = func

    def register_blueprints_from_list(self, blueprints):
        for blueprint in blueprints:
            self.app.register_blueprint(blueprint)

    @staticmethod
    def provide_models():
        return []

    @staticmethod
    def provide_blueprints():
        return []

    @staticmethod
    def provide_filters():
        return {}

    def init_models(self, *args, **kwargs):
        return self.provide_models()

    def init_blueprints(self, *args, **kwargs):
        self.register_blueprints_from_list(self.provide_blueprints())

    def init_filters(self, *args, **kwargs):
        self.register_filters_from_dict(self.provide_filters())

    def introduce(self, *args, **kwargs):
        return getattr(self, 'NAME', 'unknown')

    def view_admin_extensions(self, *args, **kwargs):
        return ExtensionView.from_class(self.__class__)
