"""
TODO:
 - decorator
 - thread local cache instance - but shared
 - arbitrary user-specified cache keys
 - filesystem OPTIONAL
 - locking
 - Keyer scheme
 - per-module-ish CACHE_VERSION convention
 - are pickles stable?
 - ComputeCache class
 - Cacheable - fn is one
 - ttl
 - nice to have: np mmap
 - compress?
 - decos, descriptors, etc
 - overlap w/ jobs/dags/batches/whatever
 - joblib
 - keep src anyway, but just for warn
"""
import contextlib
import functools
import tempfile
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')
CacheT = ta.TypeVar('CacheT', bound='Cache')


##


@dc.dataclass(frozen=True)
class CacheKey(lang.Final):
    version: int
    fn: ta.Callable
    args: tuple
    kwargs: col.frozendict[str, ta.Any]

    @dc.validate
    def _check_types(self) -> bool:
        return (
                isinstance(self.version, int) and self.version >= 0 and
                callable(self.fn) and
                isinstance(self.args, tuple) and
                isinstance(self.kwargs, col.frozendict)
        )


class Cache:
    def __init__(self, base_dir: str) -> None:
        super().__init__()

        self._base_dir = base_dir

        self._dct: dict[CacheKey, ta.Any] = {}

    def get(self, key: CacheKey) -> lang.Maybe[ta.Any]:
        try:
            ret = self._dct[key]
        except KeyError:
            return lang.empty()
        else:
            return lang.just(ret)

    def put(self, key: CacheKey, val: ta.Any) -> None:
        self._dct[key] = val


##


_CURRENT_CACHE: Cache | None = None


@contextlib.contextmanager
def cache_context(cache: CacheT) -> ta.Iterator[CacheT]:
    global _CURRENT_CACHE
    prev = _CURRENT_CACHE
    try:
        _CURRENT_CACHE = cache
        yield
    finally:
        _CURRENT_CACHE = prev


def cached(version: int) -> ta.Callable[[T], T]:
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            if (cache := _CURRENT_CACHE) is not None:
                key = CacheKey(
                    version,
                    fn,
                    args,
                    col.frozendict(kwargs),
                )

                if (hit := cache.get(key)).present:
                    return hit.must()

                val = fn(*args, **kwargs)
                cache.put(key, val)
                return val

            else:
                return fn(*args, **kwargs)
        return inner
    return outer


##


@cached(0)
def f(x: int, y: int) -> int:
    print(f'f({x}, {y})')
    return x + y


@cached(0)
def g(x: int, y: int) -> int:
    print(f'g({x}, {y})')
    return f(x, 1) + f(y, 1)


def _main() -> None:
    assert g(1, 2) == 5

    #

    tmp_dir = tempfile.mkdtemp()
    print(f'{tmp_dir=}')

    cache = Cache(tmp_dir)

    #

    with cache_context(cache):
        for _ in range(2):
            assert g(1, 2) == 5


if __name__ == '__main__':
    _main()
