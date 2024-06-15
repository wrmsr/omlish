import glob
import imp
import importlib
import importlib.abc
import importlib.machinery
import os.path
import shutil
import sys
import sysconfig

from . import _distutils as du


class CExtensionLoader(importlib.abc.Loader):

    def __init__(self, fullname: str, path: str) -> None:
        super().__init__()

        self._fullname = fullname
        self._path = path

    def load_module(self, fullname):
        extra_link_args = []
        if sys.platform == 'darwin':
            extra_link_args.append('-Wl,-no_fixup_chains')

        ext = du.Extension(
            self._fullname,
            sources=[self._path],
            extra_compile_args=['-std=c++14'],
            extra_link_args=extra_link_args,
            undef_macros=['BARF'],
        )

        cmd_obj = du.BuildExt(du.BuildExt.Options(
            inplace=True,
            debug=True,
        ))
        cmd_obj.build_extension(ext)

        so_path = os.path.join(
            os.path.dirname(self._path),
            ''.join([
                fullname.rpartition('.')[2],
                '.',
                sysconfig.get_config_var('SOABI'),
                sysconfig.get_config_var('SHLIB_SUFFIX'),
            ]),
        )
        return imp.load_dynamic(self._fullname, so_path)


loader_details = (CExtensionLoader, ['.c', '.cc', '.cpp', '.cxx'])


def install():
    sys.path_hooks.insert(0, importlib.machinery.FileFinder.path_hook(loader_details))
    sys.path_importer_cache.clear()
    importlib.invalidate_caches()


##


def barf(x: object) -> str:
    """hi i do barf"""
    return f'barf str! {x!r}'


def return_barf(ty):
    return barf


def _main():
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    install()

    ##

    from . import junk  # noqa
    print(junk.junk())
    print(junk.abctok())

    ##

    import functools

    print(os.getpid())
    # input()

    from . import _dispatch  # noqa
    fw = functools.wraps(barf)(_dispatch.function_wrapper(return_barf))

    print(fw)
    print(fw.dispatch)
    assert fw(10) == 'barf str! 10'

    import weakref
    fwr = weakref.ref(fw)
    assert fwr() is fw

    import pickle
    upfw = pickle.loads(pickle.dumps(fw))
    assert upfw(10) == 'barf str! 10'


if __name__ == '__main__':
    _main()
