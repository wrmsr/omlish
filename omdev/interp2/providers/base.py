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
from .inspect import InterpInspector
from .types import Interp
from .types import InterpSpecifier
from .types import InterpVersion


##


class InterpProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    @abc.abstractmethod
    def installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
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
        return InterpInspector.running().iv

    def installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    def installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return []

    def get_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=sys.executable,
            provider=self.name,
            version=self.version(),
        )
