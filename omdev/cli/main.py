"""
TODO:
 - cache ldr.discover() somehow if in uvx/pipx - very slow
  - <venv-root>/.omdev-cli-manifest-cache.json - {pkg_name: manifests_json}
 - allow manually specifying manifest packages
"""
import argparse
import os
import runpy
import sys
import typing as ta

from omlish import check

from ..manifests.load import ManifestLoader
from .types import CliCmd
from .types import CliFunc
from .types import CliModule


##


def _post_install(cli_pkg: str) -> None:
    from .managers import setup_install_manager

    setup_install_manager(cli_pkg)


##


_CLI_FUNCS: ta.Sequence[CliFunc] = [
    CliFunc('_post_install', _post_install),
]


##


def _main() -> None:
    ccs: list[CliCmd] = []

    #

    ldr = ManifestLoader.from_entry_point(globals())

    pkgs = ldr.discover()

    if not pkgs:
        pkgs = []
        for n in os.listdir(os.getcwd()):
            if os.path.isdir(n) and os.path.exists(os.path.join(n, '__init__.py')):
                pkgs.append(n)

    for m in ldr.load(*pkgs, only=[CliModule]):
        ccs.append(check.isinstance(m.value, CliModule))

    #

    ccs.extend(_CLI_FUNCS)

    #

    dct: dict[str, CliCmd] = {}
    for cc in ccs:
        if cc.cmd_name in dct:
            raise NameError(cc)
        dct[cc.cmd_name] = cc

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs='?', choices=dct.keys())
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    #

    cc = dct[args.cmd]

    if isinstance(cc, CliModule):
        sys.argv = [cc.cmd_name, *(args.args or ())]
        runpy._run_module_as_main(cc.mod_name)  # type: ignore  # noqa

    elif isinstance(cc, CliFunc):
        cc.fn(*(args.args or ()))

    else:
        raise TypeError(cc)


if __name__ == '__main__':
    _main()
