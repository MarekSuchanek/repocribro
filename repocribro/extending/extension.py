import abc
import pkg_resources
import sys


class Extension(abc.ABC):

    @abc.abstractmethod
    def call(self, hook_name, args, **kwargs):
        pass


class ExtensionsMaster:
    ENTRYPOINT_GROUP = 'repocribro.ext'
    LOAD_ERROR_MSG = 'Extension "{}" ({}) is not making an Extension ' \
                     '(sub)class instance. It will be ignored!'

    @classmethod
    def _collect_extensions(cls, name=None):
        return pkg_resources.iter_entry_points(
            group=cls.ENTRYPOINT_GROUP, name=name
        )

    # TODO: there might be some problem with ordering of extensions
    def __init__(self, *args, **kwargs):
        entry_points = self._collect_extensions()
        self.exts = []
        for ep in entry_points:
            ext_maker = ep.load()
            e = ext_maker(*args, **kwargs)
            if not isinstance(e, Extension):
                print(self.LOAD_ERROR_MSG.format(
                    ep.name, ep.module_name, file=sys.stderr
                ))
            else:
                self.exts.append(e)

    def call(self, hook_name, default=None, *args, **kwargs):
        return [ext.call(hook_name, default, args, **kwargs)
                for ext in self.exts]
