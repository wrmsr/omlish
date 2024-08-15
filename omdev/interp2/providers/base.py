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

from omlish.lite.cached import cached_nullary
from .inspect import InterpInspector
from .types import Interp
from .types import InterpSpecifier
from .types import InterpVersion


##


class InterpProvider(abc.ABC):
    @abc.abstractmethod
    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_installed_version(self, version: InterpVersion) -> Interp:
        raise NotImplementedError

    def get_installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return []

    def install_version(self, version: InterpVersion) -> Interp:
        raise TypeError


##


class RunningInterpProvider(InterpProvider):
    @cached_nullary
    def version(self) -> InterpVersion:
        return InterpInspector.running().iv

    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    def get_installed_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=sys.executable,
            version=self.version(),
        )
