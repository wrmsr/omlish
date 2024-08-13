"""
Reqs:
 - backends
  - system
  - running
  - pyenv
  - local builds
  - indygreg
  - deadsnakes?
 - loose versions

SEE:
 - https://github.com/tusharsadhwani/yen/blob/8d1bb0c1232c7b0159caefb1bf3a5348b93f7b43/src/yen/github.py
 - https://github.com/pypa/pipx/blob/4fbbe9c7c83740b33aa306e48435ea0e8c96c769/src/pipx/interpreter.py
"""
# ruff: noqa: UP007
import abc
import dataclasses as dc
import json
import sys
import typing as ta

from ...amalg.std.cached import cached_nullary
from ...amalg.std.subprocesses import subprocess_check_output
from ...amalg.std.versions.versions import Version
from ...amalg.std.versions.versions import parse_version


##


@dc.dataclass(frozen=True)
class InterpVersion:
    version: Version
    debug: bool = False
    threaded: bool = False


@dc.dataclass(frozen=True)
class Interp:
    exe: str
    provider: str
    version: InterpVersion


##


_RAW_QUERY_INTERP_VERSION_CODE = """
__import__('json').dumps(dict(
    version=__import__('sys').version,
    debug=bool(__import__('sysconfig').get_config_var('Py_DEBUG')),
    threaded=bool(__import__('sysconfig').get_config_var('Py_GIL_DISABLED')),
))"""

_QUERY_INTERP_VERSION_CODE = ''.join(l.strip() for l in _RAW_QUERY_INTERP_VERSION_CODE.splitlines())


def _translate_queried_interp_version(out: str) -> InterpVersion:
    dct = json.loads(out)
    return InterpVersion(
        parse_version(dct['version'].split()[0]),
        debug=dct['debug'],
        threaded=dct['threaded'],
    )


def query_interp_exe_version(path: str) -> InterpVersion:
    out = subprocess_check_output(path, '-c', f'print({_QUERY_INTERP_VERSION_CODE})')
    return _translate_queried_interp_version(out.decode())


##


class InterpProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    @abc.abstractmethod
    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError


##


class RunningInterpProvider(InterpProvider):
    @property
    def name(self) -> str:
        return 'running'

    @cached_nullary
    def version(self) -> InterpVersion:
        out = eval(_QUERY_INTERP_VERSION_CODE)  # noqa
        return _translate_queried_interp_version(out)

    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        return []

    def get_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=sys.executable,
            provider=self.name,
            version=self.version(),
        )
