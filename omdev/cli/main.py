"""
TODO:
 - py/foo - root command 'py'
 - cache ldr.discover() somehow if in uvx/pipx - very slow
  - <venv-root>/.omdev-cli-manifest-cache.json - {pkg_name: manifests_json}
 - allow manually specifying manifest packages
"""
import argparse
import dataclasses as dc
import os
import runpy
import sys
import typing as ta

from omlish import check
from omlish.lite.cached import cached_nullary

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


StrTuple: ta.TypeAlias = tuple[str, ...]
RecStrMap: ta.TypeAlias = ta.Mapping[str, ta.Union[str, 'RecStrMap']]
RecCmdMap: ta.TypeAlias = ta.Mapping[str, ta.Union[CliCmd, 'RecCmdMap']]


class CliCmdSet:
    def __init__(self, cmds: ta.Iterable[CliCmd]) -> None:
        super().__init__()

        self._cmds = list(cmds)

    @dc.dataclass(frozen=True)
    class Entry:
        cmd: CliCmd

        exec_paths: ta.Sequence[StrTuple]  # len > 1, len([0]) > 1
        help_path: StrTuple | None

    def _make_entry(self, cmd: CliCmd) -> Entry:
        help_path: StrTuple | None

        if isinstance(cmd.cmd_name, str):
            ns = [cmd.cmd_name]
        else:
            ns = cmd.cmd_name
        exec_paths = [tuple(n.split('/')) for n in ns]

        if isinstance(cmd.cmd_name, str) and cmd.cmd_name[0] == '_':
            help_path = None

        elif isinstance(cmd, CliFunc):
            help_path = ('-', *exec_paths[0])

        elif isinstance(cmd, CliModule):
            help_path = (cmd.mod_name.partition('.')[0], *exec_paths[0])

        else:
            raise TypeError(cmd)

        return CliCmdSet.Entry(
            cmd,

            exec_paths=exec_paths,
            help_path=help_path,
        )

    @cached_nullary
    def entries(self) -> ta.Sequence[Entry]:
        return [self._make_entry(c) for c in self._cmds]

    @cached_nullary
    def exec_tree(self) -> RecCmdMap:
        d: dict = {}
        for e in self.entries():
            for ep in e.exec_paths:
                c = d
                for p in ep[:-1]:
                    n = c.setdefault(p, {})
                    if not isinstance(n, dict):
                        raise NameError(e)
                    c = n

                h = ep[-1]
                if h in c:
                    raise NameError(e)

                c[h] = e.cmd

        return d

    @cached_nullary
    def help_tree(self) -> RecStrMap:
        d: dict = {}
        for e in self.entries():
            if not e.help_path:
                continue

            c = d
            for p in e.help_path[:-1]:
                n = c.setdefault(p, {})
                if not isinstance(n, dict):
                    raise NameError(e)
                c = n

            h = e.help_path[-1]
            if h in c:
                raise NameError(e)

            if isinstance(e.cmd.cmd_name, str):
                l = [e.cmd.cmd_name]
            else:
                l = list(e.cmd.cmd_name)

            s = (
                f'{l[0].split("/")[-1]}'
                f'{(" (" + ", ".join(l[1:]) + ")") if len(l) > 1 else ""}'
            )

            c[h] = s

        return d

    def select_cmd(self, args: ta.Sequence[str]) -> tuple[CliCmd, ta.Sequence[str]] | None:
        check.not_isinstance(args, str)
        raise NotImplementedError


##


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli-pkg-root', action='append')
    parser.add_argument('--cli-debug', action='store_true')
    parser.add_argument('cmd', nargs='?')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    return parser


def _build_cmd_dct(args: ta.Any) -> ta.Mapping[str, CliCmd]:
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

    #

    lst: list[CliCmd] = []

    for m in ldr.load(*pkgs, only=[CliModule]):
        lst.append(check.isinstance(m.value, CliModule))

    lst.extend(_CLI_FUNCS)

    #

    ccs = CliCmdSet(lst)

    print(ccs.help_tree())
    print(ccs.exec_tree())

    breakpoint()

    #

    dct: dict[str, CliCmd] = {}
    mdct: dict[str, dict[str, CliCmd]] = {}
    for cc in ccs:
        for cn in [cc.cmd_name] if isinstance(cc.cmd_name, str) else cc.cmd_name:
            if cn in dct:
                raise NameError(cc)
            if '/' in cn:
                l, r = cn.split('/')
                sdct = mdct.setdefault(l, {})
                if r in sdct:
                    raise NameError(cc)
                sdct[r] = cc
            else:
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

    def inner():
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

    if args.cli_debug:
        from omlish.diag.debug import debugging_on_exception

        with debugging_on_exception():
            return inner()

    else:
        return inner()


if __name__ == '__main__':
    sys.exit(rc if isinstance(rc := _main(), int) else 0)
