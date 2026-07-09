"""Tests for cached_function's pluggable backing map (the `map_maker` opt) and reset semantics."""
import collections
import functools

from ..function import cached_function


##


def test_nullary_map_is_none():
    @cached_function
    def f():
        return 1

    assert f() == 1
    assert f._values is None  # type: ignore  # noqa


def test_default_map_is_dict():
    @cached_function
    def f(x):
        return x + 1

    assert f(1) == 2
    assert type(f._values) is dict  # type: ignore  # noqa


def test_custom_map_maker():
    @cached_function(map_maker=collections.OrderedDict)
    def f(x):
        return x

    assert f(1) == 1
    assert isinstance(f._values, collections.OrderedDict)  # type: ignore  # noqa
    assert dict(f._values) == {1: 1}  # type: ignore  # noqa


def test_none_is_cached():
    n = 0

    @cached_function
    def f():
        nonlocal n
        n += 1
        return None  # noqa

    assert f() is None
    assert f() is None
    assert n == 1


def test_reset_recomputes():
    n = 0

    @cached_function
    def f():
        nonlocal n
        n += 1
        return n

    assert f() == 1
    assert f() == 1
    f.reset()  # type: ignore
    assert f() == 2
    assert f() == 2


def test_reset_preserves_map_type():
    # Regression: reset() must rebuild the backing map via map_maker, not replace it with a bare dict.
    @cached_function(map_maker=collections.OrderedDict)
    def f(x):
        return x

    assert f(1) == 1
    assert isinstance(f._values, collections.OrderedDict)  # type: ignore  # noqa
    f.reset()  # type: ignore
    assert isinstance(f._values, collections.OrderedDict)  # type: ignore  # noqa
    assert f(2) == 2
    assert dict(f._values) == {2: 2}  # type: ignore  # noqa


def test_collections_cache_eviction():
    from ....collections import cache

    seen = []

    @cached_function(map_maker=functools.partial(cache.new_cache, max_size=2))
    def f(x):
        seen.append(x)
        return x * 10

    assert f(1) == 10
    assert f(2) == 20
    assert f(1) == 10  # still resident
    assert seen == [1, 2]
    assert f(3) == 30  # evicts LRU (2)
    assert f(2) == 20  # recomputed
    assert seen == [1, 2, 3, 2]
