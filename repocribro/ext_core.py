from .extending import Extension


class CoreExtension(Extension):
    NAME = 'core'
    CATEGORY = 'basic'

    def __init__(self, *args, **kwargs):
        pass

    def call(self, hook_name, *args, **kwargs):
        if hook_name == 'introduce':
            return self.NAME


def make_extension(*args, **kwargs):
    return CoreExtension(*args, **kwargs)
