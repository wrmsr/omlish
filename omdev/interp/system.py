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

from omlish.lite.cached import cached_nullary
from omlish.lite.logs import log

from ..packaging.versions import InvalidVersion
from .inspect import INTERP_INSPECTOR
from .inspect import InterpInspector
from .providers import InterpProvider
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

    def get_exe_version(self, exe: str) -> ta.Optional[InterpVersion]:
        if not self.inspect:
            s = os.path.basename(exe)
            if s.startswith('python'):
                s = s[len('python'):]
            if '.' in s:
                try:
                    return InterpVersion.parse(s)
                except InvalidVersion:
                    pass
        ii = self.inspector.inspect(exe)
        return ii.iv if ii is not None else None

    def exe_versions(self) -> ta.Sequence[ta.Tuple[str, InterpVersion]]:
        lst = []
        for e in self.exes():
            if (ev := self.get_exe_version(e)) is None:
                log.debug('Invalid system version: %s', e)
                continue
            lst.append((e, ev))
        return lst

    #

    def get_installed_versions(self, spec: InterpSpecifier) -> ta.Sequence[InterpVersion]:
        return [ev for e, ev in self.exe_versions()]

    def get_installed_version(self, version: InterpVersion) -> Interp:
        for e, ev in self.exe_versions():
            if ev != version:
                continue
            return Interp(
                exe=e,
                version=ev,
            )
        raise KeyError(version)
