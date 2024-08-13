"""
TODO:
 - python, python3, python3.12, ...
"""
# ruff: noqa: UP006 UP007
import dataclasses as dc
import os
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
    path: ta.Optional[str] = None

    @property
    def name(self) -> str:
        return 'system'

    @staticmethod
    def _which(
            cmd: str,
            *,
            mode: int = os.F_OK | os.X_OK,
            path: ta.Optional[str] = None,
    ) -> ta.Optional[str]:
        if path is None:
            path = os.environ.get('PATH', None)
            if path is None:
                try:
                    path = os.confstr('CS_PATH')
                except (AttributeError, ValueError):
                    path = os.defpath

        if not path:
            return None

        path = os.fsdecode(path)
        pathlst = path.split(os.pathsep)

        def _access_check(fn: str, mode: int) -> bool:
            return (os.path.exists(fn) and os.access(fn, mode) and not os.path.isdir(fn))

        files = [cmd]
        seen = set()
        for d in pathlst:
            normdir = os.path.normcase(d)
            if normdir not in seen:
                seen.add(normdir)
                for thefile in files:
                    name = os.path.join(d, thefile)
                    if _access_check(name, mode):
                        return name

        return None

    @cached_nullary
    def exe(self) -> ta.Optional[str]:
        return self._which(self.cmd, path=self.path)

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
