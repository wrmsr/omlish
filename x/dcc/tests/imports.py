import importlib
import importlib.abc
import importlib.machinery
import sys


class MyLoader(importlib.abc.SourceLoader):

    def __init__(self, fullname: str, path: str) -> None:
        super().__init__()

        self._fullname = fullname
        self._path = path

    def get_filename(self, fullname: str) -> str:
        return self._path

    def get_data(self, filename: str) -> str:
        """exec_module is already defined for us, we just have to provide a way
        of getting the source code of the module"""
        with open(filename) as f:
            data = f.read()
        # do something with data ...
        # eg. ignore it... return 'print('hello world')'
        return data


loader_details = MyLoader, ['.c', '.cc', '.cpp', '.cxx']


def install():
    sys.path_hooks.insert(0, importlib.machinery.FileFinder.path_hook(loader_details))
    sys.path_importer_cache.clear()
    importlib.invalidate_caches()
