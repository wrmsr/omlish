import enum
import os.path
import site
import sys


##


def _normalize_pkg_name(s: str) -> str:
    return s.lower().replace('_', '-')


##


class ManagerType(enum.Enum):
    UVX = 'uvx'
    PIPX = 'pipx'


def detect_install_manager(cli_pkg: str) -> ManagerType | None:
    if os.path.isfile(fp := os.path.join(sys.prefix, 'uv-receipt.toml')):
        import tomllib

        with open(fp) as f:
            dct = tomllib.loads(f.read())

        reqs = dct.get('tool', {}).get('requirements')
        main_pkg = _normalize_pkg_name(reqs[0].get('name', ''))
        if reqs and main_pkg == cli_pkg:
            return ManagerType.UVX

    if os.path.isfile(fp := os.path.join(sys.prefix, 'pipx_metadata.json')):
        import json

        with open(fp) as f:
            dct = json.loads(f.read())

        main_pkg = _normalize_pkg_name(dct.get('main_package', {}).get('package_or_url', ''))
        if main_pkg == cli_pkg:
            return ManagerType.PIPX

    return None


##
# Python is insistent on prepending sys.path with an empty string (translating to the current working directory),
# which leads to problems when using the cli in directories containing python packages (such as within this very
# source tree). This can't be done in cli main as the code frequently spawns other sys.executable processes which
# wouldn't know to do that, so a .pth file hack is used. Cleaning sys.path solely there is also insufficient as that
# code runs before the problematic empty string is added, so a sys.meta_path hook is prepended.
#
# See:
#   https://github.com/python/cpython/blob/da1e5526aee674bb33c17a498aa3781587b9850c/Python/sysmodule.c#L3939


def _remove_empty_from_sys_path() -> None:
    while '' in sys.path:
        sys.path.remove('')


class _PathHackMetaFinder:
    def find_spec(self, fullname, path, target=None):
        _remove_empty_from_sys_path()
        return None  # noqa


def _activate_path_hack() -> None:
    if not any(isinstance(mp, _PathHackMetaFinder) for mp in sys.meta_path):
        sys.meta_path.insert(0, _PathHackMetaFinder())


_PATH_HACK_FILE_NAME = f'{"-".join(__name__.split("."))}-path-hack.pth'


def _install_path_hack_file() -> None:
    sp = site.getsitepackages()[0]
    if os.path.isfile(fp := os.path.join(sp, _PATH_HACK_FILE_NAME)):
        return

    with open(fp, 'w') as f:
        f.write(f'import {__name__}; {__name__}._activate_path_hack()')

    _activate_path_hack()


##


def setup_install_manager(cli_pkg: str) -> None:
    if detect_install_manager(cli_pkg) is None:
        return

    _install_path_hack_file()
