"""
TODO:
 - python, python3, python3.12, ...
 - check if path py's are venvs: sys.prefix != sys.base_prefix
"""
# ruff: noqa: UP006 UP007
import dataclasses as dc
import os
import re
import typing as ta

from ...amalg.std.cached import cached_nullary
from ...amalg.std.logs import log
from ...amalg.std.check import check_not_none
from .base import InterpProvider
from .inspect import INTERP_INSPECTOR
from .inspect import InterpInspector
from .types import Interp
from .types import InterpSpecifier
from .types import InterpVersion


##


@dc.dataclass(frozen=True)
class SystemInterpProvider(InterpProvider):
    cmd: str = 'python3'
    path: ta.Optional[str] = None

    inspect: bool = False
    inspector: InterpInspector = INTERP_INSPECTOR

    @property
    def name(self) -> str:
        return 'system'

    #

    @staticmethod
    def _re_which(
            pat: re.Pattern,
            *,
            mode: int = os.F_OK | os.X_OK,
            path: ta.Optional[str] = None,
    ) -> ta.List[str]:
        if path is None:
            path = os.environ.get('PATH', None)
            if path is None:
                try:
                    path = os.confstr('CS_PATH')
                except (AttributeError, ValueError):
                    path = os.defpath

        if not path:
            return []

        path = os.fsdecode(path)
        pathlst = path.split(os.pathsep)

        def _access_check(fn: str, mode: int) -> bool:
            return os.path.exists(fn) and os.access(fn, mode)

        out = []
        seen = set()
        for d in pathlst:
            normdir = os.path.normcase(d)
            if normdir not in seen:
                seen.add(normdir)
                if not _access_check(normdir, mode):
                    continue
                for thefile in os.listdir(d):
                    name = os.path.join(d, thefile)
                    if not (
                            os.path.isfile(name) and
                            pat.fullmatch(thefile) and
                            _access_check(name, mode)
                    ):
                        continue
                    out.append(name)

        return out

    @cached_nullary
    def exes(self) -> ta.List[str]:
        return self._re_which(
            re.compile(r'python3(\.\d+)?'),
            path=self.path,
        )

    #

    def exe_version(self, exe: str) -> ta.Optional[InterpVersion]:
        if self.inspect:
            return self.inspector.inspect(exe).iv
        s = os.path.basename(exe)
        if s.startswith('python'):
            s = s[len('python'):]
        if '.' not in s:
            return self.inspector.inspect(exe).iv
        return InterpVersion.parse(s)

    @cached_nullary
    def exe_versions(self) -> ta.Sequence[ta.Tuple[str, InterpVersion]]:
        lst = []
        for e in self.exes():
            if (ev := self.exe_version(e)) is None:
                log.debug('Invalid guessed system version: %s', e)
                continue
            lst.append((e, ev))
        return lst

    #

    def installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [ev for e, ev in self.exe_versions()]

    def installable_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return []

    def get_version(self, version: InterpVersion) -> Interp:
        for e, ev in self.exe_versions():
            if ev.version != version:
                continue
            return Interp(
                exe=e,
                provider=self.name,
                version=ev,
            )
        raise KeyError(version)
