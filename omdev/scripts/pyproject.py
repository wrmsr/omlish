#!/usr/bin/env python3
"""
TODO:
 - check / tests, src dir sets
 - ci
 - build / package / publish

lookit:
 - https://pdm-project.org/en/latest/
 - https://rye.astral.sh/philosophy/
 - https://github.com/indygreg/python-build-standalone/blob/main/pythonbuild/cpython.py
 - https://astral.sh/blog/uv
 - https://github.com/jazzband/pip-tools
"""
import argparse
import dataclasses as dc
import functools
import itertools
import logging
import os.path
import shlex
import shutil
import subprocess
import sys
import typing as ta


T = ta.TypeVar('T')


log = logging.getLogger(__name__)


REQUIRED_PYTHON_VERSION = (3, 8)


INTERP_SCRIPT = 'omdev/scripts/interp.py'


##


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


def _toml_loads(s: str) -> ta.Any:
    toml: ta.Any = None
    try:
        import tomllib as toml
    except ImportError:
        try:
            from pip._vendor import tomli as toml  # noqa
        except ImportError:
            pass
    if toml is not None:
        return toml.loads(s)

    if shutil.which('toml2json') is None:
        subprocess.check_call(['cargo', 'install', 'toml2json'])
    jsonb = subprocess.check_output(['toml2json'], input=s.encode())

    import json
    return json.loads(jsonb.decode().strip())


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


def _find_docker_service_container(cfg_path: str, svc_name: str) -> str:
    out = subprocess.check_output(['docker-compose', '-f', cfg_path, 'ps', '-q', svc_name])
    return out.decode().strip()


def _get_interp_exe(s: str, *, interp_script: str = INTERP_SCRIPT) -> str:
    if not s.startswith('@'):
        return s
    dbg_sfx = '-debug'
    if s.endswith(dbg_sfx):
        s, dbg = s[:-len(dbg_sfx)], True
    else:
        dbg = False
    raw_vers = _read_versions_file()
    pfx = 'PYTHON_'
    vers = {k[len(pfx):].lower(): v for k, v in raw_vers.items() if k.startswith(pfx)}
    ver = vers[s[1:]]
    exe = subprocess.check_output([
        sys.executable,
        interp_script,
        'resolve',
        *(['--debug'] if dbg else []),
        ver,
    ]).decode().strip()
    return exe


@cached_nullary
def _script_rel_path() -> str:
    cwd = os.getcwd()
    if not (f := __file__).startswith(cwd):
        raise EnvironmentError(f'file {f} not in {cwd}')
    return f[len(cwd):].lstrip(os.sep)


##


@dc.dataclass()
class VenvSpec:
    name: str
    interp: ta.Optional[str] = None
    requires: ta.Union[str, ta.List[str], None] = None
    docker: ta.Optional[str] = None


def _build_venv_specs(cfgs: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, VenvSpec]:
    venv_specs = {n: VenvSpec(name=n, **vs) for n, vs in cfgs.items()}
    if (all_venv_spec := venv_specs.pop('all')) is not None:
        avkw = dc.asdict(all_venv_spec)
        for n, vs in list(venv_specs.items()):
            vskw = {**avkw, **{k: v for k, v in dc.asdict(vs).items() if v is not None}}
            venv_specs[n] = VenvSpec(**vskw)
    return venv_specs


class Venv:
    def __init__(self, spec: VenvSpec) -> None:
        if spec.name == 'all':
            raise Exception
        super().__init__()
        self._spec = spec

    @property
    def spec(self) -> VenvSpec:
        return self._spec

    DIR_NAME_PREFIX = '.venv'
    DIR_NAME_SEP = '-'

    @property
    def dir_name(self) -> str:
        if (n := self._spec.name) == 'default':
            return self.DIR_NAME_PREFIX
        return ''.join([self.DIR_NAME_PREFIX, self.DIR_NAME_SEP, n])

    @cached_nullary
    def interp_exe(self) -> str:
        return _get_interp_exe(_check_not_none(self._spec.interp))

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

        log.info(f'Using interpreter {(ie := self.interp_exe())}')
        subprocess.check_call([ie, '-m' 'venv', dn])

        ve = self.exe()

        if (sr := self._spec.requires):
            subprocess.check_call([
                ve,
                '-m', 'pip',
                'install',
                *itertools.chain.from_iterable(['-r', r] for r in ([sr] if isinstance(sr, str) else sr)),
            ])

        return True


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
            with open('pyproject.toml', 'r') as f:
                buf = f.read()
        elif isinstance(self._raw_cfg, str):
            buf = self._raw_cfg
        else:
            return self._raw_cfg
        return _toml_loads(buf)

    @cached_nullary
    def venvs(self) -> ta.Mapping[str, Venv]:
        venv_specs = _build_venv_specs(self.raw_cfg()['tool']['omlish']['pyproject']['venvs'])
        return {n: Venv(vs) for n, vs in venv_specs.items()}


##


def _venv_cmd(args) -> None:
    venv = Run().venvs()[args.name]
    if (sd := venv.spec.docker) is not None and sd != (cd := args._docker_container):  # noqa
        ctr = _find_docker_service_container('docker/docker-compose.yml', sd)
        script = ' '.join([
            'python3',
            shlex.quote(_script_rel_path()),
            f'--_docker_container={shlex.quote(sd)}',
            *map(shlex.quote, sys.argv[1:]),
        ])
        call_args = ['docker', 'exec', '-it', ctr, 'bash', '--login', '-c', script]
        subprocess.check_call(call_args)
        return

    venv.create()
    print(venv.exe())


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--_docker_container')

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('venv')
    parser_resolve.add_argument('name')
    parser_resolve.set_defaults(func=_venv_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    # FIXME: -v
    # logging.root.addHandler(logging.StreamHandler())
    # logging.root.setLevel('INFO')

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
