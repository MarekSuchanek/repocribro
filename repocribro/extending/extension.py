import abc
import pkg_resources


class Extension(abc.ABC):

    @abc.abstractmethod
    def call(self, hook_name, args, **kwargs):
        pass


class ExtensionsMaster:
    ENTRYPOINT_GROUP = 'repocribro.ext'

    @classmethod
    def _collect_extensions(cls, name=None):
        return pkg_resources.iter_entry_points(
            group=cls.ENTRYPOINT_GROUP, name=name
        )

    def __init__(self, *args, **kwargs):
        entry_points = self._collect_extensions()
        self.exts = []
        for ep in entry_points:
            ext_maker = ep.load()
            e = ext_maker(*args, **kwargs)
            if not isinstance(e, Extension):
                print('Extension {} not making an Extension instance'.format(
                    ep.module_name
                ))
            else:
                self.exts.append(e)

    def call(self, hook_name, *args, **kwargs):
        return [ext.call(hook_name, args, **kwargs) for ext in self.exts]
