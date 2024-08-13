# ruff: noqa: UP007
import dataclasses as dc
import shutil
import typing as ta

from ...amalg.std.cached import cached_nullary
from .base import Interp
from .base import InterpProvider
from .base import InterpVersion
from .base import query_interp_exe_version


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
        return query_interp_exe_version(exe)

    def installed_versions(self) -> ta.Sequence[InterpVersion]:
        return [self.version()]

    def installable_versions(self) -> ta.Sequence[InterpVersion]:
        return []

    def get_version(self, version: InterpVersion) -> Interp:
        if version != self.version():
            raise KeyError(version)
        return Interp(
            exe=self.exe(),
            provider=self.name,
            version=self.version(),
        )
