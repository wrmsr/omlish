"""
Features:
 - get (line, offset)
 - invalidate
  - filewatcher
 - linecache interop
  - tokenize.open - detect encoding - only for .py
 - directory / path_parts tree?

TODO:
 - 1-based?
 - maximums?
  - lru? max_size/max_entries?
   - collections.cache?

Notes:
 - linecache is 1-based
 - linecache appends final newline if missing:
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'
"""
import dataclasses as dc
import os.path
import stat as stat_
import tokenize
import typing as ta

from .. import cached
from .. import check
from .. import lang
from ..os.paths import abs_real_path


##


class TextFileCache:
    class FileStat(ta.NamedTuple):
        size: int
        mtime: float

    class Entry:
        def __init__(
                self,
                cache: 'TextFileCache',
                path: str,
                stat: 'TextFileCache.FileStat',
        ) -> None:
            super().__init__()

            self._cache = cache
            self._path = path
            self._stat = stat

        def __repr__(self) -> str:
            return lang.attr_repr(self, 'path', 'stat')

        @property
        def path(self) -> str:
            return self._path

        @property
        def stat(self) -> 'TextFileCache.FileStat':
            return self._stat

        @cached.function
        def contents(self) -> str:
            return self._cache._read_file(self._path)  # noqa

        @cached.function
        def lines(self) -> ta.Sequence[str]:
            return self.contents().splitlines(keepends=True)

        def safe_line(self, n: int, default: str = '') -> str:
            lines = self.lines()
            if 0 <= n < len(lines):
                return lines[n]
            return default

    #

    def __init__(
            self,
            *,
            locking: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._dct: dict[str, TextFileCache.Entry] = {}
        self._lock = lang.default_lock(locking)()

    #

    class Error(Exception):
        pass

    @dc.dataclass()
    class PathTypeError(Error):
        path: str

    #

    def _normalize_path(self, path: str) -> str:
        return abs_real_path(path)

    #

    def _try_stat_file(self, path: str) -> FileStat | Exception:
        try:
            st = os.stat(path)
        except FileNotFoundError as e:
            return e

        if not stat_.S_ISREG(st.st_mode):
            return TextFileCache.PathTypeError(path)

        return TextFileCache.FileStat(
            st.st_size,
            st.st_mtime,
        )

    def _read_file(self, path: str) -> str:
        if path.endswith('.py'):
            with tokenize.open(path) as f:
                return f.read()

        else:
            with open(path) as f:
                return f.read()

    #

    def _get_entry(
            self,
            path: str,
            *,
            check_stat: bool = False,
            or_raise: bool = False,
    ) -> Entry:
        st_: TextFileCache.FileStat | Exception | None = None
        try:
            e = self._dct[path]

        except KeyError:
            if or_raise:
                raise

        else:
            if (
                    not check_stat or
                    (st_ := self._try_stat_file(path)) == e.stat
            ):
                return e

            del self._dct[path]

        st: TextFileCache.FileStat | Exception
        if st_ is not None:
            st = st_
        else:
            st = self._try_stat_file(path)

        if isinstance(st, Exception):
            raise st

        e = TextFileCache.Entry(
            self,
            path,
            check.isinstance(st, TextFileCache.FileStat),
        )

        self._dct[path] = e

        return e

    def get_entry(
            self,
            path: str,
            *,
            check_stat: bool = False,
            or_raise: bool = False,
    ) -> Entry:
        path = self._normalize_path(path)

        with self._lock:
            return self._get_entry(
                path,
                check_stat=check_stat,
                or_raise=or_raise,
            )

    #

    def invalidate(self, path: str) -> bool:
        path = self._normalize_path(path)

        with self._lock:
            return self._dct.pop(path, None) is not None
