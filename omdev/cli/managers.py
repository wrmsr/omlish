import enum
import os.path
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


def setup_install_manager(cli_pkg: str) -> None:
    if detect_install_manager(cli_pkg) is None:
        return

    from ._pathhack import _install_pth_file
    _install_pth_file()
