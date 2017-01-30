from .extending import Extension
from .extending.helpers import ExtensionView


class CoreExtension(Extension):
    NAME = 'core'
    CATEGORY = 'basic'
    AUTHOR = 'Marek Suchánek'
    GH_URL = 'https://github.com/MarekSuchanek/repocribro'

    def __init__(self, app, db, *args, **kwargs):
        self.app = app
        self.db = db

    def call(self, hook_name, default, *args, **kwargs):
        invert_op = getattr(self, hook_name, None)
        if callable(invert_op):
            return invert_op(*args, **kwargs)
        else:
            return default

    def introduce(self):
        return self.NAME

    def view_admin_extensions(self):
        return ExtensionView(
            self.NAME,
            self.CATEGORY,
            self.AUTHOR,
            gh_url=self.GH_URL
        )


def make_extension(*args, **kwargs):
    return CoreExtension(*args, **kwargs)
