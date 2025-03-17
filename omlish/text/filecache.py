"""
Features:
 - get (line, offset)
 - invalidate
  - filewatcher
 - linecache interop
  - tokenize.open - detect encoding - only for .py
 - directory / path_parts tree?

TODO:
 - read raw, decode (detect)
  - ! index from byteofs -> charofs
   - charofs -> lineno
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
import io
import os.path
import stat as stat_
import tokenize
import typing as ta

from .. import cached
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
                *,
                encoding: str | None = None,
        ) -> None:
            super().__init__()

            self._cache = cache
            self._path = path
            self._stat = stat
            self._given_encoding = encoding

        def __repr__(self) -> str:
            return lang.attr_repr(self, 'path', 'stat')

        @property
        def path(self) -> str:
            return self._path

        @property
        def stat(self) -> 'TextFileCache.FileStat':
            return self._stat

        @cached.function
        def raw(self) -> bytes:
            return self._cache._read_file(self._path)  # noqa

        @cached.function
        def encoding(self) -> str:
            if (ge := self._given_encoding) is not None:
                return ge
            return self._cache._determine_encoding(self._path, self.raw())  # noqa

        @cached.function
        def text(self) -> str:
            return self.raw().decode(self.encoding())

        @cached.function
        def lines(self) -> ta.Sequence[str]:
            return self.text().splitlines(keepends=True)

        def safe_line(self, n: int, default: str = '') -> str:
            lines = self.lines()
            if 0 <= n < len(lines):
                return lines[n]
            return default

    #

    @dc.dataclass(frozen=True)
    class Config:
        max_file_size: int | None = 5 * 1024 * 1024

        default_encoding: str = 'utf-8'

    def __init__(
            self,
            config: Config = Config(),
            *,
            locking: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._config = config

        self._dct: dict[str, TextFileCache.Entry] = {}
        self._lock = lang.default_lock(locking)()

    #

    class Error(Exception):
        pass

    @dc.dataclass()
    class PathError(Error):
        path: str

    class PathTypeError(PathError):
        pass

    class FileTooBigError(PathError):
        pass

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

    def _read_file(self, path: str) -> bytes:
        with open(path, 'rb') as f:
            return f.read()

    def _determine_encoding(self, path: str, raw: bytes) -> str:
        if path.endswith('.py'):
            buf = io.BytesIO(raw)
            encoding, _ = tokenize.detect_encoding(buf.readline)
            return encoding

        return self._config.default_encoding

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

        if (mfs := self._config.max_file_size) is not None and st.size > mfs:
            raise TextFileCache.FileTooBigError(path)

        e = TextFileCache.Entry(
            self,
            path,
            st,
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
