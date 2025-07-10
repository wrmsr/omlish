import sys
import typing as ta

from omlish.lite.cached import cached_nullary

from ..inspect import InterpInspector
from ..types import Interp
from ..types import InterpSpecifier
from ..types import InterpVersion
from .base import InterpProvider


##


class RunningInterpProvider(InterpProvider):
    @cached_nullary
    def version(self) -> InterpVersion:
        return InterpInspector.running().iv

    async def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    async def get_installed_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=sys.executable,
            version=self.version(),
        )
