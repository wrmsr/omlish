#!/usr/bin/env python3
# @omdev-amalg ../scripts/pyproject2.py
"""
TODO:
 - check / tests, src dir sets
 - ci
 - build / package / publish / version roll
  - {pkg_name: [src_dirs]}, default excludes, generate MANIFST.in, ...

lookit:
 - https://pdm-project.org/en/latest/
 - https://rye.astral.sh/philosophy/
 - https://github.com/indygreg/python-build-standalone/blob/main/pythonbuild/cpython.py
 - https://astral.sh/blog/uv
 - https://github.com/jazzband/pip-tools
 - https://github.com/Osiris-Team/1JPM
 - https://github.com/brettcannon/microvenv
 - https://github.com/pypa/pipx
 - https://github.com/tox-dev/tox/
"""
# ruff: noqa: UP007
import argparse
import dataclasses as dc
import itertools
import os.path
import shlex
import shutil
import sys
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_not
from omlish.lite.check import check_not_none
from omlish.lite.logs import configure_standard_logging
from omlish.lite.runtime import check_runtime_version
from omlish.lite.subprocesses import subprocess_check_call
from omlish.lite.subprocesses import subprocess_check_output

from ..toml.toml import toml_loads
from .configs import PyprojectConfig
from .configs import PyprojectConfigPreparer
from .venvs import Venv


##


@dc.dataclass(frozen=True)
class VersionsFile:
    name: ta.Optional[str] = '.versions'

    @cached_nullary
    def contents(self) -> ta.Mapping[str, str]:
        if not self.name or not os.path.exists(self.name):
            return {}
        with open(self.name) as f:
            lines = f.readlines()
        return {
            k: v
            for l in lines
            if (sl := l.split('#')[0].strip())
            for k, _, v in (sl.partition('='),)
        }

    @cached_nullary
    def pythons(self) -> ta.Mapping[str, str]:
        raw_vers = self.contents()
        pfx = 'PYTHON_'
        return {k[len(pfx):].lower(): v for k, v in raw_vers.items() if k.startswith(pfx)}


##


def _find_docker_service_container(cfg_path: str, svc_name: str) -> str:
    out = subprocess_check_output('docker', 'compose', '-f', cfg_path, 'ps', '-q', svc_name)
    return out.decode().strip()


@cached_nullary
def _script_rel_path() -> str:
    cwd = os.getcwd()
    if not (f := __file__).startswith(cwd):
        raise OSError(f'file {f} not in {cwd}')
    return f[len(cwd):].lstrip(os.sep)


##


class Run:
    def __init__(
            self,
            *,
            raw_cfg: ta.Union[ta.Mapping[str, ta.Any], str, None] = None,
    ) -> None:
        super().__init__()

        self._raw_cfg = raw_cfg

    @cached_nullary
    def raw_cfg(self) -> ta.Mapping[str, ta.Any]:
        if self._raw_cfg is None:
            with open('pyproject.toml') as f:
                buf = f.read()
        elif isinstance(self._raw_cfg, str):
            buf = self._raw_cfg
        else:
            return self._raw_cfg
        return toml_loads(buf)

    @cached_nullary
    def cfg(self) -> PyprojectConfig:
        dct = self.raw_cfg()['tool']['omlish']['pyproject2']
        return PyprojectConfigPreparer(
            python_versions=VersionsFile().pythons(),
        ).prepare_config(dct)

    @cached_nullary
    def venvs(self) -> ta.Mapping[str, Venv]:
        return {
            n: Venv(n, c)
            for n, c in self.cfg().venvs.items()
            if not n.startswith('_')
        }


##


def _venv_cmd(args) -> None:
    venv = Run().venvs()[args.name]
    if (sd := venv.cfg.docker) is not None and sd != (cd := args._docker_container):  # noqa
        ctr = _find_docker_service_container('docker/compose.yml', sd)
        script = ' '.join([
            'python3',
            shlex.quote(_script_rel_path()),
            f'--_docker_container={shlex.quote(sd)}',
            *map(shlex.quote, sys.argv[1:]),
        ])
        subprocess_check_call(
            'docker',
            'exec',
            *itertools.chain.from_iterable(
                ('-e', f'{e}={os.environ.get(e, "")}' if '=' not in e else e)
                for e in (args.docker_env or [])
            ),
            '-it', ctr,
            'bash', '--login', '-c', script,
        )
        return

    venv.create()

    cmd = args.cmd
    if not cmd:
        pass

    elif cmd == 'exe':
        check_not(args.args)
        print(venv.exe())

    elif cmd == 'run':
        sh = check_not_none(shutil.which('bash'))
        script = ' '.join(args.args)
        if not script:
            script = sh
        os.execl(
            (bash := check_not_none(sh)),
            bash,
            '-c',
            f'. {venv.dir_name}/bin/activate && ' + script,
        )

    elif cmd == 'srcs':
        check_not(args.args)
        print('\n'.join(venv.srcs()))

    elif cmd == 'test':
        subprocess_check_call(venv.exe(), '-m', 'pytest', *(args.args or []), *venv.srcs())

    else:
        raise Exception(f'unknown subcommand: {cmd}')


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--_docker_container', help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('venv')
    parser_resolve.add_argument('name')
    parser_resolve.add_argument('-e', '--docker-env', action='append')
    parser_resolve.add_argument('cmd', nargs='?')
    parser_resolve.add_argument('args', nargs='*')
    parser_resolve.set_defaults(func=_venv_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_runtime_version()
    configure_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
