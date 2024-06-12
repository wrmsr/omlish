import glob
import imp
import importlib
import importlib.abc
import importlib.machinery
import os.path
import shutil
import sys

from . import _distutils as du


class CExtensionLoader(importlib.abc.Loader):

    def __init__(self, fullname: str, path: str) -> None:
        super().__init__()

        self._fullname = fullname
        self._path = path

    def load_module(self, fullname):
        ext = du.Extension(
            self._fullname,
            sources=[self._path],
            extra_compile_args=['-std=c++14'],
            undef_macros=['BARF'],
        )

        cmd_obj = du.BuildExt(du.BuildExt.Options(
            inplace=True,
            debug=True,
        ))
        cmd_obj.build_extension(ext)

        so_path = os.path.join(os.path.dirname(self._path), 'junk.cpython-311-darwin.so')
        return imp.load_dynamic(self._fullname, so_path)


loader_details = (CExtensionLoader, ['.c', '.cc', '.cpp', '.cxx'])


def install():
    sys.path_hooks.insert(0, importlib.machinery.FileFinder.path_hook(loader_details))
    sys.path_importer_cache.clear()
    importlib.invalidate_caches()


def _main():
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    install()

    from . import junk  # noqa
    print(junk.junk())
    print(junk.abctok())


if __name__ == '__main__':
    _main()
