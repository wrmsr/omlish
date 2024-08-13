"""
TODO:
 - backends
  - local builds
  - deadsnakes?
 - loose versions
"""
# ruff: noqa: UP007
import abc
import sys
import typing as ta

from ...amalg.std.cached import cached_nullary
from ...amalg.std.check import check_not_none
from ...amalg.std.versions.specifiers import SpecifierSet
from .inspect import INTERP_INSPECTOR
from .types import Interp
from .types import InterpVersion


##


def query_interp_exe_version(exe: str) -> InterpVersion:
    ins = check_not_none(INTERP_INSPECTOR.inspect(exe))
    return InterpVersion(
        version=ins.version,
        debug=ins.debug,
        threaded=ins.threaded,
    )


##


class InterpProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def installed_versions(self, spec: SpecifierSet) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    @abc.abstractmethod
    def installable_versions(self, spec: SpecifierSet) -> ta.Sequence[InterpVersion]:
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
        return query_interp_exe_version(sys.executable)

    def installed_versions(self, spec: SpecifierSet) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    def installable_versions(self, spec: SpecifierSet) -> ta.Sequence[InterpVersion]:
        return []

    def get_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=sys.executable,
            provider=self.name,
            version=self.version(),
        )
