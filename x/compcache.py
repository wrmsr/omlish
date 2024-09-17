"""
TODO:
 - decorator
 - thread local cache instance - but shared
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
 - decos, deescriptors, etc
"""
import tempfile
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class CacheKey(lang.Final):
    fn: ta.Callable
    args: tuple
    kwargs: col.frozendict[str, ta.Any]

    @dc.validate
    def _check_types(self) -> bool:
        return (
                callable(self.fn) and
                isinstance(self.args, tuple) and
                isinstance(self.kwargs, col.frozendict)
        )


class Cache:
    def __init__(self, base_dir: str) -> None:
        super().__init__()

        self._base_dir = base_dir

        self._dct: dict[CacheKey, ta.Any] = {}

    def get(self, key: CacheKey) -> ta.Any:
        raise NotImplementedError

    def __call__(self, fn: ta.Callable[..., T], *args: ta.Any, **kwargs: ta.Any) -> T:
        key = CacheKey(fn, args, col.frozendict(kwargs))
        try:
            return self._dct[key]
        except KeyError:
            pass
        ret = fn(*args, **kwargs)
        self._dct[key] = ret
        return ret


##


def f(x: int, y: int) -> int:
    print(f'f({x}, {y})')
    return x + y


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

    for _ in range(2):
        assert cache(g, 1, 2) == 5


if __name__ == '__main__':
    _main()
