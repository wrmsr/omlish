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
        for cn in [cc.cmd_name] if isinstance(cc.cmd_name, str) else cc.cmd_name:
            if cn in dct:
                raise NameError(cc)
            dct[cn] = cc

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs='?', choices=dct.keys())
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if not args.cmd:
        mdct: dict = {}
        for cc in ccs:
            if isinstance(cc.cmd_name, str) and cc.cmd_name[0] == '_':
                continue
            if isinstance(cc, CliFunc):
                mdct.setdefault('-', []).append(cc)
            elif isinstance(cc, CliModule):
                mdct.setdefault(cc.mod_name.partition('.')[0], []).append(cc)
            else:
                raise TypeError(cc)

        print('Subcommands:\n')
        for m, l in sorted(mdct.items(), key=lambda t: (t[0] == '-', t[0])):
            print(f'  {m}')
            for cc in sorted(l, key=lambda c: c.primary_name):
                if isinstance(cc.cmd_name, str):
                    print(f'    {cc.cmd_name}')
                else:
                    print(f'    {cc.cmd_name[0]} ({", ".join(cc.cmd_name[1:])})')
            print()
        return

    #

    cc = dct[args.cmd]

    if isinstance(cc, CliModule):
        sys.argv = [args.cmd, *(args.args or ())]
        runpy._run_module_as_main(cc.mod_name)  # type: ignore  # noqa

    elif isinstance(cc, CliFunc):
        cc.fn(*(args.args or ()))

    else:
        raise TypeError(cc)


if __name__ == '__main__':
    _main()
