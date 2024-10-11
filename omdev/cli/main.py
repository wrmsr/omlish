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


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli-pkg-root', action='append')
    parser.add_argument('cmd', nargs='?')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    return parser


def _build_cmd_dct(args: ta.Any) -> ta.Mapping[str, CliCmd]:
    ccs: list[CliCmd] = []

    ldr = ManifestLoader.from_entry_point(globals())

    pkgs: list[str] = []

    def scan_pkg_root(r: str) -> None:
        r = os.path.expanduser(r)
        for n in os.listdir(r):
            if os.path.isdir(p := os.path.join(r, n)) and os.path.exists(os.path.join(p, '__init__.py')):
                pkgs.append(n)

    if args.cli_pkg_root:
        for r in args.cli_pkg_root:
            scan_pkg_root(r)

    else:
        pkgs.extend(ldr.discover())

        if not pkgs:
            scan_pkg_root(os.getcwd())

    for m in ldr.load(*pkgs, only=[CliModule]):
        ccs.append(check.isinstance(m.value, CliModule))

    ccs.extend(_CLI_FUNCS)

    dct: dict[str, CliCmd] = {}
    for cc in ccs:
        for cn in [cc.cmd_name] if isinstance(cc.cmd_name, str) else cc.cmd_name:
            if cn in dct:
                raise NameError(cc)
            dct[cn] = cc

    return dct


def _select_cmd(args: ta.Any, cmds: ta.Mapping[str, CliCmd]) -> CliCmd | int:
    cmd = args.cmd
    if cmd and cmd in cmds:
        return cmds[cmd]

    def print_err(*args, **kwargs):  # noqa
        print(*args, **kwargs, file=sys.stderr)

    if cmd:
        print_err(f'Invalid command: {cmd}\n')
        rc = 1
    else:
        rc = 0

    mset = set()
    mdct: dict = {}
    for cc in cmds.values():
        if id(cc) in mset:
            continue
        mset.add(id(cc))
        if isinstance(cc.cmd_name, str) and cc.cmd_name[0] == '_':
            continue
        if isinstance(cc, CliFunc):
            mdct.setdefault('-', []).append(cc)
        elif isinstance(cc, CliModule):
            mdct.setdefault(cc.mod_name.partition('.')[0], []).append(cc)
        else:
            raise TypeError(cc)

    print_err('Subcommands:\n')
    for m, l in sorted(mdct.items(), key=lambda t: (t[0] == '-', t[0])):
        print_err(f'  {m}')
        for cc in sorted(l, key=lambda c: c.primary_name):
            if isinstance(cc.cmd_name, str):
                print_err(f'    {cc.cmd_name}')
            else:
                print_err(
                    f'    {cc.cmd_name[0]}'
                    f'{(" (" + ", ".join(cc.cmd_name[1:]) + ")") if len(cc.cmd_name) > 1 else ""}',
                )
        print_err()

    return rc


def _main() -> ta.Any:
    parser = _build_arg_parser()
    args = parser.parse_args()
    cmds = _build_cmd_dct(args)
    sel = _select_cmd(args, cmds)

    match sel:
        case int():
            return sel

        case CliModule() as cm:
            sys.argv = [args.cmd, *(args.args or ())]
            runpy._run_module_as_main(cm.mod_name)  # type: ignore  # noqa
            return 0

        case CliFunc() as cf:
            return cf.fn(*(args.args or ()))

        case _:
            raise TypeError(sel)


if __name__ == '__main__':
    sys.exit(rc if isinstance(rc := _main(), int) else 0)
