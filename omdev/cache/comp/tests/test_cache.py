from omlish import dataclasses as dc

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
            print()

        before = cache.stats

        f1.__cacheable__ = dc.replace(f1.__cacheable__, version=1)

        for _ in range(2):
            v = f3(1, 1)
            print(f'f3(1, 1)={v}')
            print()

        after = cache.stats

        print(f'{before=}, {after=}')