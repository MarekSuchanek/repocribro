from .helpers import ExtensionView


class Extension:
    """Generic **repocribro** extension class

    It serves as base extension which does nothing but has prepared
    all the attributes and methods needed. Particular real extensions
    can override those attributes and methods to make so behavior
    and extend repocribro. It also provides some useful methods to
    those subclasses.
    """

    #: Name of extension
    NAME = 'unknown'
    #: Category of extension (basic, security, data, ...)
    CATEGORY = ''
    #: Author(s) of extension
    AUTHOR = ''
    #: Administration URL within site (best via url_for)
    ADMIN_URL = None
    #: Homepage url of extension (rtd, pocoo, ...)
    HOME_URL = None
    #: GitHub url of extension project
    GH_URL = None

    def __init__(self, master, app, db):
        """Inits the basic two parts of repocribro - flask app and DB

        :param master: Master for this extension
        :type master: ``ExtensionsMaster``
        :param app: Flask application of repocribro
        :type app: ``flask.Flask``
        :param db: SQLAlchemy database of repocribro
        :type db: ``flask_sqlalchemy.SQLAlchemy``
        :param args: not used
        :param kwargs: not used
        """
        self.master = master
        self.app = app
        self.db = db

    def call(self, hook_name, default, *args, **kwargs):
        """Call the operation via hook name

        :param hook_name: Name of hook to be called
        :type hook_name: str
        :param default: Default return value if hook operation not found
        :param args: Positional args to be passed to the hook operation
        :param kwargs: Keywords args to be passed to the hook operation
        :return: Result of the operation on the requested hook
        """
        operation = getattr(self, hook_name, None)
        if callable(operation):
            return operation(*args, **kwargs)
        else:
            return default

    def register_filters_from_dict(self, filters):
        """Registering functions as Jinja filters

        :param filters: Dictionary where key is name of filter and
                        value is the function serving as filter
        :type filters: dict of str: function
        """
        for name, func in filters.items():
            self.app.jinja_env.filters[name] = func

    def register_blueprints_from_list(self, blueprints):
        """Registering Flask blueprints to the app

        :param blueprints: List of Flask blueprints to be registered
        :type blueprints: ``list`` of ``flask.blueprint``
        """
        for blueprint in blueprints:
            self.app.register_blueprint(blueprint)

    @staticmethod
    def provide_models():
        """Extension can provide (DB) models to the app by this method

        :return: List of models provided by extension
        :rtype: list of ``db.Model``
        """
        return []

    @staticmethod
    def provide_blueprints():
        """Extension can provide Flask blueprints to the app by this method

        :return: List of Flask blueprints provided by extension
        :rtype: list of ``flask.blueprint``
        """
        return []

    @staticmethod
    def provide_filters():
        """Extension can provide Jinja filters to the app by this method

        :return: Dictionary with name + function/filter pairs
        :rtype: dict of str: function
        """
        return {}

    def init_models(self):
        """Hook operation for initiating the models and registering them
        within db
        """
        return self.provide_models()

    def init_blueprints(self):
        """Hook operation for initiating the blueprints and registering them
        within repocribro Flask app
        """
        self.register_blueprints_from_list(self.provide_blueprints())

    def init_filters(self):
        """Hook operation for initiating the Jinja filters and registering them
        within Jinja env of repocribro Flask app
        """
        self.register_filters_from_dict(self.provide_filters())

    def introduce(self):
        """Hook operation for getting short introduction of extension (mostly
        for debug/log purpose)

        :return: Name of the extension
        :rtype: str
        """
        return getattr(self, 'NAME', 'unknown')

    def view_admin_extensions(self):
        """Hook operation for getting view model of the extension in order
        to show it in the administration of app

        :return: Extensions view for this extension
        :rtype: ``repocribro.extending.helpers.ExtensionView``
        """
        return ExtensionView.from_class(self.__class__)
