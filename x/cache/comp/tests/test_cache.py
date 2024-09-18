from omlish import check

from ..cache import Cache
from ..contexts import cache_context
from ..fns import FnCacheableResolver
from ..fns import cached_fn


@cached_fn(0)
def f0(x: int, y: int) -> int:
    print(f'f0({x}, {y})')
    return x + y


@cached_fn(0)
def f1(x: int, y: int) -> int:
    print(f'f1({x}, {y})')
    return f0(x, 1) + f0(y, 1)


@cached_fn(0)
def f2(x: int, y: int) -> int:
    print(f'f2({x}, {y})')
    return f0(x, 2) + f0(y, 1)


@cached_fn(0)
def f3(x: int, y: int) -> int:
    print(f'f3({x}, {y})')
    return f1(x, 2) + f2(y, 1)


def test_cache():
    fr = FnCacheableResolver()
    cache = Cache(resolver=fr)

    with cache_context(cache):
        print()

        for _ in range(2):
            print(f'{f3(1, 1)=}')

        before = cache.stats

