"""
TODO:
 - backends
  - local builds
  - deadsnakes?
  - uv
 - loose versions
"""
import abc
import sys
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.strings import snake_case

from .inspect import InterpInspector
from .types import Interp
from .types import InterpSpecifier
from .types import InterpVersion


##


class InterpProvider(abc.ABC):
    name: ta.ClassVar[str]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC not in cls.__bases__ and 'name' not in cls.__dict__:
            sfx = 'InterpProvider'
            if not cls.__name__.endswith(sfx):
                raise NameError(cls)
            setattr(cls, 'name', snake_case(cls.__name__[:-len(sfx)]))

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
