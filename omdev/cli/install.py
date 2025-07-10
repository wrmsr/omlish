#!/usr/bin/env python3
# ruff: noqa: UP045
# @omlish-lite
# @omlish-script
"""
curl -LsSf 'https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/cli/install.py' | python3 -
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


##


DEFAULT_CLI_PKG = 'omdev-cli'
DEFAULT_PY_VER = '3.13'


@dc.dataclass(frozen=True)
class InstallOpts:
    cli_pkg: str = DEFAULT_CLI_PKG
    cli_ver: ta.Optional[str] = None

    py_ver: str = DEFAULT_PY_VER

    extras: ta.Sequence[str] = dc.field(default_factory=list)


def _format_install_cli_pkg(opts: InstallOpts) -> str:
    spec = opts.cli_pkg
    if (ver := opts.cli_ver) is not None:
        if any(c in ver for c in '=<>!~'):
            spec += ver
        else:
            spec = f'{spec}=={ver}'
    return spec


class InstallManager(abc.ABC):
    @abc.abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def uninstall(self, cli_pkg: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, opts: InstallOpts) -> None:
        raise NotImplementedError


class UvxInstallManager(InstallManager):
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
            _format_install_cli_pkg(opts),
            *itertools.chain.from_iterable(['--with', e] for e in (opts.extras or [])),
        ])

        subprocess.check_call([
            'uv', 'tool',
            'run',
            '--from', opts.cli_pkg,
            'om',
            '_post_install',
            opts.cli_pkg,
        ])


class PipxInstallManager(InstallManager):
    def is_available(self) -> bool:
        return bool(shutil.which('pipx'))

    def _list_installed(self) -> ta.Any:
        out = subprocess.check_output(['pipx', 'list', '--json']).decode()
        return json.loads(out)

    def uninstall(self, cli_pkg: str) -> None:
        dct = self._list_installed()

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
            _format_install_cli_pkg(opts),
            *itertools.chain.from_iterable(['--preinstall', e] for e in (opts.extras or [])),
        ])

        dct = self._list_installed()

        exe = dct['venvs'][opts.cli_pkg]['metadata']['main_package']['app_paths'][0]['__Path__']

        subprocess.check_call([
            exe,
            '_post_install',
            opts.cli_pkg,
        ])


INSTALL_MANAGERS = {
    'uvx': UvxInstallManager(),
    'pipx': PipxInstallManager(),
}


def _main() -> None:
    if sys.version_info < (3, 8):  # noqa
        raise RuntimeError(f'Unsupported python version: {sys.version_info}')

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cli', default=DEFAULT_CLI_PKG)
    parser.add_argument('-V', '--version')
    parser.add_argument('-p', '--python', default=DEFAULT_PY_VER)
    parser.add_argument('-m', '--manager')
    parser.add_argument('extra', nargs='*')
    args = parser.parse_args()

    if not (cli := args.cli):
        raise ValueError(f'Must specify cli')

    cli = cli.lower().replace('_', '-')

    if not (py := args.python):
        raise ValueError(f'Must specify py')

    if mgr := args.manager:
        if (im := INSTALL_MANAGERS.get(mgr)) is None:
            raise ValueError(f'Unsupported mgr: {mgr}')
        if not im.is_available():
            raise ValueError(f'Unavailable mgr: {mgr}')
    else:
        for im in INSTALL_MANAGERS.values():
            if im.is_available():
                break
        else:
            raise RuntimeError("Can't find install manager")

    for m in INSTALL_MANAGERS.values():
        if m.is_available():
            m.uninstall(cli)

    im.install(InstallOpts(
        cli_pkg=cli,
        cli_ver=args.version,
        py_ver=py,
        extras=args.extra,
    ))


if __name__ == '__main__':
    _main()
