import abc
import contextlib
import functools
import importlib
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')
CacheT = ta.TypeVar('CacheT', bound='Cache')


##




##






##


@cached_fn(0)
def f(x: int, y: int) -> int:
    print(f'f({x}, {y})')
    return x + y


@cached_fn(0)
def g(x: int, y: int) -> int:
    print(f'g({x}, {y})')
    return f(x, 1) + f(y, 1)


@cached_fn(0)
def h(x: int, y: int) -> int:
    print(f'g({x}, {y})')
    return g(x, 2) + g(y, 2)


def _main() -> None:
    fr = CachingCacheableResolver(FnCacheableResolver())

    h_fc = h.__cacheable__
    h_fcn = h_fc.name
    check.is_(fr.resolve(h_fcn), h_fc)

    #

    # check.equal(h(1, 2), 11)

    #

    cache = Cache(resolver=fr)

    #

    with cache_context(cache):
        for _ in range(2):
            print(f'{(v := h(1, 2))=}')
            check.equal(v, 11)

            print(f'{(v := h(3, 2))=}')
            check.equal(v, 13)

        print()


if __name__ == '__main__':
    _main()
