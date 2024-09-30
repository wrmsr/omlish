import enum
import os.path
import site
import sys


##


class ManagerType(enum.Enum):
    UVX = 'uvx'
    PIPX = 'pipx'


def _detect_install_manager() -> ManagerType | None:
    if os.path.isfile(fp := os.path.join(sys.prefix, 'uv-receipt.toml')):
        with open(fp) as f:
            if any(l.strip() == '[tool]' for l in f):
                return ManagerType.UVX

    if os.path.isfile(os.path.join(sys.prefix, 'pipx_metadata.json')):
        return ManagerType.PIPX

    return None


def detect_install_manager() -> ManagerType | None:
    try:
        return globals()['_DETECTED_MANAGER_TYPE']
    except KeyError:
        pass
    ret = globals()['_DETECTED_MANAGER_TYPE'] = _detect_install_manager()
    return ret


##


def _ensure_correct_path() -> None:
    sp = site.getsitepackages()[0]
    if sys.path[0] != sp:
        sys.path.insert(0, sp)


class _PathHackMetaFinder:
    def find_spec(self, fullname, path, target=None):
        _ensure_correct_path()
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


def setup_install_manager() -> None:
    if detect_install_manager() is None:
        return

    _install_path_hack_file()
