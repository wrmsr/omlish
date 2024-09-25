#!/usr/bin/env python3
"""
TODO:
 - usable as 'curl -LsSf https://raw.githubusercontent.com/wrmsr/omlish/master/x/cli_install.py | python3'
 - used for self-reinstall, preserving non-root dists

==

if uv --version 2>/dev/null ; then \
    MGR="uv tool" ; \
    INST="install --refresh --prerelease=allow --python=${INSTALL_PYTHON_VERSION}"; \
    INJ="--with" ; \
else \
    MGR="pipx" ; \
    INST="install"; \
    INJ="--preinstall" ; \
fi ; \
\
CMD="$$MGR uninstall omdev-cli || true ; $$MGR $$INST omdev-cli" ; \
for D in ${INSTALL_EXTRAS} ; do \
    CMD+=" $$INJ $$D" ; \
done ; \
${SHELL} -c "$$CMD"
"""
import abc
import argparse
import dataclasses as dc
import itertools
import shutil
import subprocess
import sys
import typing as ta


DEFAULT_CLI_PKG = 'omdev-cli'
DEFAULT_PY_VERSION = '3.12'


@dc.dataclass(frozen=True)
class InstallOpts:
    cli_pkg: str
    py_version: str
    extras: ta.Sequence[str] = dc.field(default_factory=list, kw_only=True)


class InstallMgr(abc.ABC):
    @abc.abstractmethod
    def uninstall(self, cli_pkg: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, opts: InstallOpts) -> None:
        raise NotImplementedError


class UvInstallMgr(InstallMgr):
    def uninstall(self, cli_pkg: str) -> None:
        out = subprocess.check_output(['uv', 'tool', 'list']).decode()

        inst = {
            s.partition(' ')[0]
            for l in out.splitlines()
            if (s := l.strip())
            and not s.startswith('-')
        }

        if cli_pkg not in inst:
            return

        subprocess.check_call([
            'uv', 'tool',
            'uninstall', cli_pkg,
        ])

    def install(self, opts: InstallOpts) -> None:
        subprocess.run([
            'uv', 'tool',
            'install',
            '--refresh',
            '--prerelease=allow',
            f'--python={opts.py_version}',
            opts.cli_pkg,
            *itertools.chain.from_iterable(['--with', e] for e in (opts.extras or [])),
        ])


def _install_pipx(
        cli: str,
        py: str,
        *,
        extras: ta.Sequence[str],
) -> None:
    raise NotImplementedError


def _main() -> None:
    if sys.version_info < (3, 8):
        raise RuntimeError(f'Unsupported python version: {sys.version_info}')

    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', default=DEFAULT_CLI_PKG)
    parser.add_argument('--py', default=DEFAULT_PY_VERSION)
    parser.add_argument('--mgr')
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

    if mgr == 'uv':
        _install_uv(
            cli,
            py,
            extras=args.extra,
        )

    elif mgr == 'pipx':
        _install_pipx(
            cli,
            py,
            extras=args.extra,
        )

    else:
        raise ValueError(f'Unsupported mgr: {mgr}')


if __name__ == '__main__':
    _main()
