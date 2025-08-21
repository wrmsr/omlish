"""
Python is insistent on prepending sys.path with an empty string (translating to the current working directory), which
leads to problems when using the cli in directories containing python packages (such as within this very source tree).
This can't be done in cli main as the code frequently spawns other sys.executable processes which wouldn't know to do
that, so a .pth file hack is used. Cleaning sys.path solely there is also insufficient as that code runs before the
problematic empty string is added, so a sys.meta_path hook is prepended.

See:
  https://github.com/python/cpython/blob/da1e5526aee674bb33c17a498aa3781587b9850c/Python/sysmodule.c#L3939
  https://github.com/python/cpython/blob/db0a1b8c1291bf1aa9e016e43bc2f7ed0acf83bd/Modules/getpath.py
  https://github.com/python/cpython/blob/db0a1b8c1291bf1aa9e016e43bc2f7ed0acf83bd/Modules/getpath.c
  https://github.com/python/cpython/blob/db0a1b8c1291bf1aa9e016e43bc2f7ed0acf83bd/Doc/library/sys_path_init.rst
"""
import os.path
import site
import sys


##


class _PathHackMetaFinder:
    def __init__(
            self,
            removed_paths=None,  # type: list[str] | None
    ) -> None:
        super().__init__()

        if removed_paths is None:
            removed_paths = ['', '.', os.getcwd()]
        self._removed_paths = removed_paths
        self.remove_paths()

    def remove_paths(self) -> None:
        for p in self._removed_paths:
            while p in sys.path:
                sys.path.remove(p)

    def find_spec(self, fullname, path, target=None):
        self.remove_paths()
        return None  # noqa


def _activate_path_hack() -> None:
    if not any(isinstance(mp, _PathHackMetaFinder) for mp in sys.meta_path):
        sys.meta_path.insert(0, _PathHackMetaFinder())


_PTH_FILE_NAME = f'omlish-{"-".join(__package__.split(".")[1:])}-pathhack.pth'


def _install_pth_file() -> None:
    sp = site.getsitepackages()[0]
    if os.path.isfile(fp := os.path.join(sp, _PTH_FILE_NAME)):
        return

    with open(fp, 'w') as f:
        f.write(f'import {__name__}; {__name__}._activate_path_hack()')

    _activate_path_hack()
