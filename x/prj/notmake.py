#!/usr/bin/env python3
"""
TODO:
 - import pip._vendor.tomli?

lookit:
 - https://pdm-project.org/en/latest/
 - https://rye.astral.sh/philosophy/
 - https://github.com/indygreg/python-build-standalone/blob/main/pythonbuild/cpython.py
 - https://astral.sh/blog/uv
 - https://github.com/jazzband/pip-tools


Responsibilities:
 - pyenv (./interp)
 - venvs
 - deps
 - docker
 - tests
 - checks
 - ci

Configs:
 - project
 - main_sources
 - all_sources
 - python versions (or .versions file), aliased to venvs
 - requirements txt
 - docker-compose file

==

Venv:
  interp
  requires
  docker[_container]

test_srcs ?
"""
import argparse
import functools
import logging
import os.path
import shutil
import subprocess
import sys
import typing as ta


T = ta.TypeVar('T')


log = logging.getLogger(__name__)


REQUIRED_PYTHON_VERSION = (3, 8)


def _check_not_none(v: ta.Optional[T]) -> T:
    if v is None:
        raise ValueError
    return v


class cached_nullary:
    def __init__(self, fn):
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)
    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value
    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


##


def _venv_cmd(args) -> None:
    name = args.name

    if os.path.exists(name):
        if os.path.isfile(name):
            raise Exception(f'{name} exists but is not a directory!')
        return

    interp = args.interp
    if interp[0] == '@':
        # interp_py = os.path.join(os.path.dirname(__file__), 'interp.py')
        interp_py = os.path.join(os.path.dirname(__file__), '../../omdev/scripts/interp.py')
        interp = subprocess.check_output([sys.executable, interp_py, 'resolve', interp[1:]]).decode().strip()
        log.info(f'Using interpreter {interp}')

    subprocess.check_output([interp, '-mvenv', name])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('venv')
    parser_resolve.add_argument('name')
    parser_resolve.add_argument('interp')
    parser_resolve.add_argument('--debug', action='store_true')
    parser_resolve.set_defaults(func=_venv_cmd)

    return parser


@cached_nullary
def _read_versions_file(file_name: str = '.versions') -> ta.Mapping[str, str]:
    with open(file_name, 'r') as f:
        lines = f.readlines()
    return {
        k: v
        for l in lines
        if (sl := l.split('#')[0].strip())
        for k, _, v in (sl.partition('='),)
    }


_TEST_TOML = """
[tool.notmake.venvs]
all = { interp = "@11", requires = "requirements-dev.txt" }
default = { interp = "@11", requires = "requirements-ext.txt"  }
docker = { docker = "omlish-dev" }
docker-amd64 = { docker = "omlish-dev-amd64" }
debug = { interp = "@11-debug" }
"12" = { interp = "@12" }
"13" = { interp = "@13" }
"""


@cached_nullary
def _load_toml() -> ta.Any:
    try:
        import tomllib as toml
    except ImportError:
        from pip._vendor import tomli as toml  # noqa
    return toml.loads(_TEST_TOML)


def _find_service_container(cfg_path: str, svc_name: str) -> str:
    out = subprocess.check_output(['docker-compose', '-f', cfg_path, 'ps', '-q', svc_name])
    return out.decode().strip()


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    print(_read_versions_file())
    print(_load_toml())
    print(_find_service_container('docker/docker-compose.yml', 'omlish-dev'))

    ##

    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
