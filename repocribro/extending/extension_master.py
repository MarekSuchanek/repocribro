import pkg_resources
import sys

from .extension import Extension


class ExtensionsMaster:
    """Collector & master of Extensions

    Extension master finds and holds all the **repocribro** extensions
    and is used for calling operations on them and collecting the results.

    :var ENTRYPOINT_GROUP: String used for looking up the extensions
    :var LOAD_ERROR_MSG: Error message mask for extension load error
    """
    ENTRYPOINT_GROUP = 'repocribro.ext'
    LOAD_ERROR_MSG = 'Extension "{}" ({}) is not making an Extension ' \
                     '(sub)class instance. It will be ignored!'

    @classmethod
    def _collect_extensions(cls, name=None):
        """Method for selecting extensions within ``ENTRYPOINT_GROUP``

        :param name: Can be used to select single entrypoint/extension
        :type name: str
        :return: Generator of selected entry points
        :rtype: ``pkg_resources.WorkingSet.iter_entry_points``

        """
        return pkg_resources.iter_entry_points(
            group=cls.ENTRYPOINT_GROUP, name=name
        )

    # TODO: there might be some problem with ordering of extensions
    def __init__(self, *args, **kwargs):
        """Collects all the extensions to be mantained by this object

        :param args: positional args to be passed to extensions
        :param kwargs: keywords args to be passed to extensions
        """
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
        """Call the hook on all extensions registered

        :param hook_name: Name of hook to be called
        :type hook_name: str
        :param default: Default return value if hook operation not found
        :param args: Positional args to be passed to the hook operation
        :param kwargs: Keywords args to be passed to the hook operation
        :return: Result of the operation on the requested hook
        """
        return [ext.call(hook_name, default, args, **kwargs)
                for ext in self.exts]