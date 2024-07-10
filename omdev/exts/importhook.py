"""
TODO:
 - remove imp
 - whitelist packages
"""
import imp
import importlib
import importlib.abc
import importlib.machinery
import sys

from . import build


# def load_dynamic(name, path, file=None):
#     import importlib.machinery
#     loader = importlib.machinery.ExtensionFileLoader(name, path)
#
#     # Issue #24748: Skip the sys.modules check in _load_module_shim;
#     # always load new extension
#     spec = importlib.machinery.ModuleSpec(
#         name=name, loader=loader, origin=path)
#     return _load(spec)


class CExtensionLoader(importlib.abc.Loader):

    def __init__(self, fullname: str, path: str) -> None:
        super().__init__()

        self._fullname = fullname
        self._path = path

    def load_module(self, fullname):
        so_path = build.build_ext(fullname, self._path)
        return imp.load_dynamic(self._fullname, so_path)


loader_details = (CExtensionLoader, ['.c', '.cc', '.cpp', '.cxx'])


def install():
    sys.path_hooks.insert(0, importlib.machinery.FileFinder.path_hook(loader_details))
    sys.path_importer_cache.clear()
    importlib.invalidate_caches()
