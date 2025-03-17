"""
TODO:
 - reserver / generator

==

@dc.dataclass()
class _ReservedFilenameEntry:
    unique_id: str
    seq: int = 0


_RESERVED_FILENAME_UUID_THREAD_LOCAL = threading.local()


def reserve_filename(prefix: str) -> str:
    try:
        e = _RESERVED_FILENAME_UUID_THREAD_LOCAL.unique_id
    except AttributeError:
        e = _RESERVED_FILENAME_UUID_THREAD_LOCAL.unique_id = _ReservedFilenameEntry(str(uuid.uuid4()))
    while True:
        unique_filename = f'<generated:{prefix}:{e.seq}>'
        cache_line = (1, None, (e.unique_id,), unique_filename)
        e.seq += 1
        if linecache.cache.setdefault(unique_filename, cache_line) == cache_line:
            return unique_filename
"""
import typing as ta


##


class LinecacheKey(ta.NamedTuple):
    size: int  # os.stat().st_size
    mtime: float | None  # os.stat().st_mtime
    lines: ta.Sequence[str]
    fullname: str


LinecacheLazyLoader: ta.TypeAlias = tuple[ta.Callable[[], str]]

LinecacheEntry: ta.TypeAlias = LinecacheKey | LinecacheLazyLoader


class LinecacheProtocol(ta.Protocol):
    @property
    def cache(self) -> ta.MutableMapping[str, LinecacheEntry]: ...

    def clearcache(self) -> None: ...

    def getline(
        self,
        filename: str,
        lineno: int,
        module_globals: ta.Mapping[str, ta.Any] | None = None,
    ) -> str: ...

    def getlines(
        self,
        filename: str,
        module_globals: ta.Mapping[str, ta.Any] | None = None,
    ) -> ta.Sequence[str]: ...

    def checkcache(
        self,
        filename: str | None = None,
    ) -> None: ...

    def updatecache(
        self,
        filename: str,
        module_globals: ta.Mapping[str, ta.Any] | None = None,
    ) -> ta.Sequence[str]: ...

    def lazycache(
        self,
        filename: str,
        module_globals: ta.Mapping[str, ta.Any],
    ) -> bool: ...
