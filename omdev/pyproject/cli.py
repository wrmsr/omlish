#!/usr/bin/env python3
# @omdev-amalg ../scripts/pyproject.py
# ruff: noqa: UP006 UP007
"""
TODO:
 - check / tests, src dir sets
 - ci
 - build / package / publish / version roll
  - {pkg_name: [src_dirs]}, default excludes, generate MANIFST.in, ...
 - env vars - PYTHONPATH

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
import argparse
import concurrent.futures as cf
import dataclasses as dc
import functools
import glob
import itertools
import multiprocessing as mp
import os.path
import shlex
import shutil
import sys
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_not
from omlish.lite.check import check_not_none
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log
from omlish.lite.runtime import check_runtime_version
from omlish.lite.subprocesses import subprocess_check_call

from ..interp.resolvers import DEFAULT_INTERP_RESOLVER
from ..interp.types import InterpSpecifier
from ..toml.parser import toml_loads
from .configs import PyprojectConfig
from .configs import PyprojectConfigPreparer
from .configs import VenvConfig
from .pkg import PyprojectPackageGenerator


##


@dc.dataclass(frozen=True)
class VersionsFile:
    name: ta.Optional[str] = '.versions'

    @staticmethod
    def parse(s: str) -> ta.Mapping[str, str]:
        return {
            k: v
            for l in s.splitlines()
            if (sl := l.split('#')[0].strip())
            for k, _, v in (sl.partition('='),)
        }

    @cached_nullary
    def contents(self) -> ta.Mapping[str, str]:
        if not self.name or not os.path.exists(self.name):
            return {}
        with open(self.name) as f:
            s = f.read()
        return self.parse(s)

    @staticmethod
    def get_pythons(d: ta.Mapping[str, str]) -> ta.Mapping[str, str]:
        pfx = 'PYTHON_'
        return {k[len(pfx):].lower(): v for k, v in d.items() if k.startswith(pfx)}

    @cached_nullary
    def pythons(self) -> ta.Mapping[str, str]:
        return self.get_pythons(self.contents())


##


@cached_nullary
def _script_rel_path() -> str:
    cwd = os.getcwd()
    if not (f := __file__).startswith(cwd):
        raise OSError(f'file {f} not in {cwd}')
    return f[len(cwd):].lstrip(os.sep)


##


class Venv:
    def __init__(
            self,
            name: str,
            cfg: VenvConfig,
    ) -> None:
        super().__init__()
        self._name = name
        self._cfg = cfg

    @property
    def cfg(self) -> VenvConfig:
        return self._cfg

    DIR_NAME = '.venvs'

    @property
    def dir_name(self) -> str:
        return os.path.join(self.DIR_NAME, self._name)

    @cached_nullary
    def interp_exe(self) -> str:
        i = InterpSpecifier.parse(check_not_none(self._cfg.interp))
        return DEFAULT_INTERP_RESOLVER.resolve(i).exe

    @cached_nullary
    def exe(self) -> str:
        ve = os.path.join(self.dir_name, 'bin/python')
        if not os.path.isfile(ve):
            raise Exception(f'venv exe {ve} does not exist or is not a file!')
        return ve

    @cached_nullary
    def create(self) -> bool:
        if os.path.exists(dn := self.dir_name):
            if not os.path.isdir(dn):
                raise Exception(f'{dn} exists but is not a directory!')
            return False

        log.info('Using interpreter %s', (ie := self.interp_exe()))
        subprocess_check_call(ie, '-m', 'venv', dn)

        ve = self.exe()

        subprocess_check_call(
            ve,
            '-m', 'pip',
            'install', '-v', '--upgrade',
            'pip',
            'setuptools',
            'wheel',
        )

        if (sr := self._cfg.requires):
            subprocess_check_call(
                ve,
                '-m', 'pip',
                'install', '-v',
                *sr,
            )

        return True

    @staticmethod
    def _resolve_srcs(raw: ta.List[str]) -> ta.List[str]:
        out: list[str] = []
        seen: ta.Set[str] = set()
        for r in raw:
            es: list[str]
            if any(c in r for c in '*?'):
                es = list(glob.glob(r, recursive=True))
            else:
                es = [r]
            for e in es:
                if e not in seen:
                    seen.add(e)
                    out.append(e)
        return out

    @cached_nullary
    def srcs(self) -> ta.Sequence[str]:
        return self._resolve_srcs(self._cfg.srcs or [])


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
        dct = self.raw_cfg()['tool']['omlish']['pyproject']
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
        script = ' '.join([
            'python3',
            shlex.quote(_script_rel_path()),
            f'--_docker_container={shlex.quote(sd)}',
            *map(shlex.quote, sys.argv[1:]),
        ])
        subprocess_check_call(
            'docker',
            'compose',
            '-f', 'docker/compose.yml',
            'exec',
            *itertools.chain.from_iterable(
                ('-e', f'{e}={os.environ.get(e, "")}' if '=' not in e else e)
                for e in (args.docker_env or [])
            ),
            '-it', sd,
            'bash', '--login', '-c', script,
        )
        return

    cmd = args.cmd
    if not cmd:
        venv.create()

    elif cmd == 'python':
        venv.create()
        os.execl(
            (exe := venv.exe()),
            exe,
            *args.args,
        )

    elif cmd == 'exe':
        venv.create()
        check_not(args.args)
        print(venv.exe())

    elif cmd == 'run':
        venv.create()
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
        venv.create()
        subprocess_check_call(venv.exe(), '-m', 'pytest', *(args.args or []), *venv.srcs())

    else:
        raise Exception(f'unknown subcommand: {cmd}')


##


def _pkg_cmd(args) -> None:
    run = Run()

    cmd = args.cmd
    if not cmd:
        raise Exception('must specify command')

    elif cmd == 'gen':
        build_root = os.path.join('.pkg')

        if os.path.exists(build_root):
            shutil.rmtree(build_root)

        build_output_dir = 'dist'
        run_build = bool(args.build)

        if run_build:
            os.makedirs(build_output_dir, exist_ok=True)

        num_threads = max(mp.cpu_count() // 2, 1)
        with cf.ThreadPoolExecutor(num_threads) as ex:
            futs = [
                ex.submit(functools.partial(
                    PyprojectPackageGenerator(
                        dir_name,
                        build_root,
                    ).gen,
                    run_build=run_build,
                    build_output_dir=build_output_dir,
                ))
                for dir_name in run.cfg().pkgs
            ]
            for fut in futs:
                fut.result()

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
    parser_resolve.add_argument('args', nargs=argparse.REMAINDER)
    parser_resolve.set_defaults(func=_venv_cmd)

    parser_resolve = subparsers.add_parser('pkg')
    parser_resolve.add_argument('-b', '--build', action='store_true')
    parser_resolve.add_argument('cmd', nargs='?')
    parser_resolve.add_argument('args', nargs=argparse.REMAINDER)
    parser_resolve.set_defaults(func=_pkg_cmd)

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
