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

TODO:
 - https://packaging.pypa.io/en/latest/version.html#packaging.version.Version ?
"""
# ruff: noqa: UP007
import abc
import dataclasses as dc
import shutil
import sys
import sysconfig
import typing as ta

from ...amalg.std.cached import cached_nullary
from ...amalg.std.subprocesses import subprocess_try_output


InterpVersionNum = tuple[int, ...]  # ta.TypeAlias


@dc.dataclass(frozen=True)
class InterpVersion:
    num: InterpVersionNum
    debug: bool = False
    threaded: bool = False


@dc.dataclass(frozen=True)
class Interp:
    version: InterpVersion
    provider: str
    path: str


def query_interp_exe_version_num(path: str) -> ta.Optional[InterpVersionNum]:
    out = subprocess_try_output([path, '--version'], try_=True)
    if out is None:
        return None
    ps = out.decode('utf-8').strip().splitlines()[0].split()
    if ps[0] != 'Python':
        return None
    return tuple(map(int, ps[1].split('.')))


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
        return InterpVersion(
            tuple(map(int, sys.version_info)),
            debug=bool(sysconfig.get_config_var('Py_DEBUG')),
            threaded=bool(sysconfig.get_config_var('Py_GIL_DISABLED')),
        )

    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        return []

    def get_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            self.version(),
            self.name,
            sys.executable,
        )


##


@dc.dataclass(frozen=True)
class SystemInterpProvider(InterpProvider):
    cmd: str = 'python3'

    @property
    def name(self) -> str:
        return 'system'

    @cached_nullary
    def exe(self) -> ta.Optional[str]:
        return shutil.which(self.cmd)

    @cached_nullary
    def version(self) -> ta.Optional[InterpVersion]:
        if (exe := self.exe()) is None:
            return None
        return query_interp_exe_version_num(exe)

    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    def get_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError
