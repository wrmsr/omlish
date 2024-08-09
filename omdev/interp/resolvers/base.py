# ruff: noqa: UP007
import shutil
import sys
import typing as ta

from ..cmd import cmd


class InterpResolver:

    def __init__(
            self,
            version: str,
            *,
            debug: bool = False,
            include_current_python: bool = False,
    ) -> None:
        if version is not None and not (isinstance(version, str) and version.strip()):
            raise ValueError(f'version: {version!r}')
        if not isinstance(debug, bool):
            raise TypeError(f'debug: {debug!r}')

        super().__init__()

        self._version = version.strip()
        self._debug = debug
        self._include_current_python = include_current_python

    def _get_python_ver(self, bin_path: str) -> ta.Optional[str]:
        s = cmd([bin_path, '--version'], try_=True)
        if s is None:
            return None
        ps = s.strip().splitlines()[0].split()
        if ps[0] != 'Python':
            return None
        return ps[1]

    def _resolve_which_python(self) -> ta.Optional[str]:
        wp = shutil.which('python3')
        if wp is None:
            return None
        wpv = self._get_python_ver(wp)
        if wpv == self._version:
            return wp
        return None

    def _resolve_current_python(self) -> ta.Optional[str]:
        if sys.version.split()[0] == self._version:
            return sys.executable
        return None

    def _resolvers(self) -> ta.Sequence[ta.Callable[[], ta.Optional[str]]]:
        return [
            self._resolve_which_python,
            *((self._resolve_current_python,) if self._include_current_python else ()),
        ]

    def resolve(self) -> ta.Optional[str]:
        for fn in self._resolvers():
            p = fn()
            if p is not None:
                return p
        return None
