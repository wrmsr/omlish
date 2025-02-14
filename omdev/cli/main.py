"""
TODO:
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
from omlish.manifests.load import ManifestLoader

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
            ns = list(cmd.cmd_name)
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
                        raise NameError(e)  # noqa
                    c = n

                h = ep[-1]
                if h in c:
                    raise NameError(e)  # noqa

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
                    raise NameError(e)  # noqa
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

    class SelectedCmd(ta.NamedTuple):
        cmd: CliCmd
        args: ta.Sequence[str]

    class InvalidCmd(ta.NamedTuple):
        path: ta.Sequence[str]

    def select_cmd(self, args: ta.Sequence[str]) -> SelectedCmd | InvalidCmd:
        check.not_isinstance(args, str)

        d = self.exec_tree()
        for i in range(len(args)):
            n = args[i]
            if n not in d:
                return CliCmdSet.InvalidCmd(args[:i + 1])

            c = d[n]

            if isinstance(c, CliCmd):
                return CliCmdSet.SelectedCmd(c, args[i + 1:])
            elif isinstance(c, ta.Mapping):
                d = c
            else:
                raise TypeError(c)

        return CliCmdSet.InvalidCmd([])


##


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli-pkg-root', action='append')
    parser.add_argument('--cli-debug', action='store_true')
    parser.add_argument('cmd', nargs='?')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    return parser


def _build_cmd_set(args: ta.Any) -> CliCmdSet:
    ldr = ManifestLoader.from_entry_point(globals())

    #

    pkgs = ldr.scan_or_discover_pkgs(
        specified_roots=args.cli_pkg_root,
        fallback_root=os.getcwd(),
    )

    #

    lst: list[CliCmd] = []

    for m in ldr.load(*pkgs, only=[CliModule]):
        lst.append(check.isinstance(m.value, CliModule))

    lst.extend(_CLI_FUNCS)

    #

    return CliCmdSet(lst)


def _select_cmd(args: ta.Any, cmds: CliCmdSet) -> CliCmdSet.SelectedCmd | int:
    def print_err(*args, **kwargs):  # noqa
        print(*args, **kwargs, file=sys.stderr)

    if args.cmd:
        sel_cmd = cmds.select_cmd([args.cmd, *args.args])
        if isinstance(sel_cmd, CliCmdSet.SelectedCmd):
            return sel_cmd
        elif isinstance(sel_cmd, CliCmdSet.InvalidCmd):
            print_err(f'Invalid command: {" ".join(sel_cmd.path)}\n')
        else:
            raise TypeError(sel_cmd)
        rc = 1
    else:
        rc = 0

    print_err('Subcommands:\n')

    def rec(d, pfx=''):
        for k, v in sorted(d.items(), key=lambda t: t[0]):
            if isinstance(v, str):
                print_err(pfx + v)
            else:
                print_err(pfx + k)
                rec(v, pfx + '  ')
            if not pfx:
                print_err('')

    rec(cmds.help_tree())

    return rc


def _main() -> ta.Any:
    parser = _build_arg_parser()
    args = parser.parse_args()

    def inner():
        cmds = _build_cmd_set(args)
        sel = _select_cmd(args, cmds)

        if isinstance(sel, int):
            return sel

        cmd = sel.cmd
        if isinstance(cmd, CliModule):
            sys.argv = [args.cmd, *(sel.args or ())]
            runpy._run_module_as_main(cmd.mod_name)  # type: ignore  # noqa
            return 0

        elif isinstance(cmd, CliFunc):
            return cmd.fn(*(sel.args or ()))

        else:
            raise TypeError(cmd)

    if args.cli_debug:
        from omlish.diag.debug import debugging_on_exception

        with debugging_on_exception():
            return inner()

    else:
        return inner()


if __name__ == '__main__':
    sys.exit(rc if isinstance(rc := _main(), int) else 0)
