#!/usr/bin/env python3
# @omlish-lite
# @omlish-script
"""
TODO:
 - used for self-reinstall, preserving non-root dists - fix list_root_dists

==

curl -LsSf https://raw.githubusercontent.com/wrmsr/omlish/master/x/cli_install.py | python3
"""
import abc
import argparse
import dataclasses as dc
import itertools
import json
import shutil
import subprocess
import sys
import typing as ta


DEFAULT_CLI_PKG = 'omdev-cli'
DEFAULT_PY_VER = '3.12'


@dc.dataclass(frozen=True)
class InstallOpts:
    cli_pkg: str = DEFAULT_CLI_PKG
    py_ver: str = DEFAULT_PY_VER

    extras: ta.Sequence[str] = dc.field(default_factory=list)


class InstallMgr(abc.ABC):
    @abc.abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def uninstall(self, cli_pkg: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, opts: InstallOpts) -> None:
        raise NotImplementedError


class UvInstallMgr(InstallMgr):
    def is_available(self) -> bool:
        return bool(shutil.which('uv'))

    def uninstall(self, cli_pkg: str) -> None:
        out = subprocess.check_output(['uv', 'tool', 'list']).decode()

        installed = {
            s.partition(' ')[0]
            for l in out.splitlines()
            if (s := l.strip())
            and not s.startswith('-')
        }

        if cli_pkg not in installed:
            return

        subprocess.check_call([
            'uv', 'tool',
            'uninstall',
            cli_pkg,
        ])

    def install(self, opts: InstallOpts) -> None:
        subprocess.check_call([
            'uv', 'tool',
            'install',
            '--refresh',
            '--prerelease=allow',
            f'--python={opts.py_ver}',
            opts.cli_pkg,
            *itertools.chain.from_iterable(['--with', e] for e in (opts.extras or [])),
        ])


class PipxInstallMgr(InstallMgr):
    def is_available(self) -> bool:
        return bool(shutil.which('pipx'))

    def uninstall(self, cli_pkg: str) -> None:
        out = subprocess.check_output(['pipx', 'list', '--json']).decode()

        dct = json.loads(out)

        if cli_pkg not in dct.get('venvs', {}):
            return

        subprocess.check_call([
            'pipx',
            'uninstall',
            cli_pkg,
        ])

    def install(self, opts: InstallOpts) -> None:
        subprocess.check_call([
            'pipx',
            'install',
            f'--python={opts.py_ver}',
            opts.cli_pkg,
            *itertools.chain.from_iterable(['--preinstall', e] for e in (opts.extras or [])),
        ])


INSTALL_MGRS = {
    'uv': UvInstallMgr(),
    'pipx': PipxInstallMgr(),
}


def _main() -> None:
    if sys.version_info < (3, 8):  # noqa
        raise RuntimeError(f'Unsupported python version: {sys.version_info}')

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cli', default=DEFAULT_CLI_PKG)
    parser.add_argument('-p', '--py', default=DEFAULT_PY_VER)
    parser.add_argument('-m', '--mgr')
    parser.add_argument('extra', nargs='*')
    args = parser.parse_args()

    if not (cli := args.cli):
        raise ValueError(f'Must specify cli')

    if not (py := args.py):
        raise ValueError(f'Must specify py')

    if not (mgr := args.mgr):
        if shutil.which('uv'):
            mgr = 'uv'
        elif shutil.which('pipx'):
            mgr = 'pipx'
        else:
            raise RuntimeError("Can't find package manager")

    if (im := INSTALL_MGRS.get(mgr)) is None:
        raise ValueError(f'Unsupported mgr: {mgr}')
    if not im.is_available():
        raise ValueError(f'Unavailable mgr: {mgr}')

    for m in INSTALL_MGRS.values():
        if m.is_available():
            m.uninstall(cli)

    im.install(InstallOpts(
        cli_pkg=cli,
        py_ver=py,
        extras=args.extra,
    ))


if __name__ == '__main__':
    _main()
