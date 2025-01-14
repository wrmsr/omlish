# @omlish-amalg ../scripts/pyproject.py
# ruff: noqa: UP006 UP007
"""
TODO:
 - check / tests, src dir sets
 - ci
 - build / package / publish / version roll
  - {pkg_name: [src_dirs]}, default excludes, generate MANIFST.in, ...
 - env vars - PYTHONPATH

See:
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
import asyncio
import concurrent.futures as cf
import dataclasses as dc
import functools
import itertools
import multiprocessing as mp
import os.path
import shlex
import shutil
import sys
import typing as ta

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd
from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.formats.toml.parser import toml_loads
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.runtime import check_lite_runtime_version
from omlish.logs.standard import configure_standard_logging

from .configs import PyprojectConfig
from .configs import PyprojectConfigPreparer
from .pkg import BasePyprojectPackageGenerator
from .pkg import PyprojectPackageGenerator
from .venvs import Venv


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


class PyprojectCli(ArgparseCli):
    _docker_container = argparse_arg('--_docker_container', help=argparse.SUPPRESS)

    @argparse_cmd(
        argparse_arg('name'),
        argparse_arg('-e', '--docker-env', action='append'),
        argparse_arg('cmd', nargs='?'),
        argparse_arg('args', nargs=argparse.REMAINDER),
    )
    async def venv(self) -> None:
        venv = Run().venvs()[self.args.name]
        if (sd := venv.cfg.docker) is not None and sd != (cd := self.args._docker_container):  # noqa
            script = ' '.join([
                'python3',
                shlex.quote(_script_rel_path()),
                f'--_docker_container={shlex.quote(sd)}',
                *map(shlex.quote, sys.argv[1:]),
            ])

            docker_env = {
                'DOCKER_HOST_PLATFORM': os.environ.get('DOCKER_HOST_PLATFORM', sys.platform),
            }
            for e in self.args.docker_env or []:
                if '=' in e:
                    k, _, v = e.split('=')
                    docker_env[k] = v
                else:
                    docker_env[e] = os.environ.get(e, '')

            await asyncio_subprocesses.check_call(
                'docker',
                'compose',
                '-f', 'docker/compose.yml',
                'exec',
                *itertools.chain.from_iterable(
                    ('-e', f'{k}={v}')
                    for k, v in docker_env.items()
                ),
                '-it', sd,
                'bash', '--login', '-c', script,
            )

            return

        cmd = self.args.cmd
        if not cmd:
            await venv.create()

        elif cmd == 'python':
            await venv.create()
            os.execl(
                (exe := venv.exe()),
                exe,
                *self.args.args,
            )

        elif cmd == 'exe':
            await venv.create()
            check.arg(not self.args.args)
            print(venv.exe())

        elif cmd == 'run':
            await venv.create()
            sh = check.not_none(shutil.which('bash'))
            script = ' '.join(self.args.args)
            if not script:
                script = sh
            os.execl(
                (bash := check.not_none(sh)),
                bash,
                '-c',
                f'. {venv.dir_name}/bin/activate && ' + script,
            )

        elif cmd == 'srcs':
            check.arg(not self.args.args)
            print('\n'.join(venv.srcs()))

        elif cmd == 'test':
            await venv.create()
            await asyncio_subprocesses.check_call(venv.exe(), '-m', 'pytest', *(self.args.args or []), *venv.srcs())

        else:
            raise Exception(f'unknown subcommand: {cmd}')

    @argparse_cmd(
        argparse_arg('-b', '--build', action='store_true'),
        argparse_arg('-r', '--revision', action='store_true'),
        argparse_arg('-j', '--jobs', type=int),
        argparse_arg('cmd', nargs='?'),
        argparse_arg('args', nargs=argparse.REMAINDER),
    )
    async def pkg(self) -> None:
        run = Run()

        cmd = self.args.cmd
        if not cmd:
            raise Exception('must specify command')

        elif cmd == 'gen':
            pkgs_root = os.path.join('.pkg')

            if os.path.exists(pkgs_root):
                shutil.rmtree(pkgs_root)

            build_output_dir = 'dist'
            run_build = bool(self.args.build)
            add_revision = bool(self.args.revision)

            if run_build:
                os.makedirs(build_output_dir, exist_ok=True)

            pgs: ta.List[BasePyprojectPackageGenerator] = [
                PyprojectPackageGenerator(
                    dir_name,
                    pkgs_root,
                )
                for dir_name in run.cfg().pkgs
            ]
            pgs = list(itertools.chain.from_iterable([pg, *pg.children()] for pg in pgs))

            num_threads = self.args.jobs or int(max(mp.cpu_count() // 1.5, 1))
            futs: ta.List[cf.Future]
            with cf.ThreadPoolExecutor(num_threads) as ex:
                futs = [ex.submit(pg.gen) for pg in pgs]
                for fut in futs:
                    fut.result()

                if run_build:
                    futs = [
                        ex.submit(functools.partial(
                            pg.build,
                            build_output_dir,
                            BasePyprojectPackageGenerator.BuildOpts(
                                add_revision=add_revision,
                            ),
                        ))
                        for pg in pgs
                    ]
                    for fut in futs:
                        fut.result()

        else:
            raise Exception(f'unknown subcommand: {cmd}')


##


async def _async_main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_lite_runtime_version()
    configure_standard_logging()

    await PyprojectCli(argv).async_cli_run()


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    asyncio.run(_async_main(argv))


if __name__ == '__main__':
    _main()
