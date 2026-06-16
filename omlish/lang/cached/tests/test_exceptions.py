"""Tests for cached_function exception caching (the `cache_exceptions` opt)."""
import pytest

from ..function import cached_function


##


class Err1(Exception):  # noqa
    pass


class Err2(Err1):  # noqa
    pass


class Err3(Exception):  # noqa
    pass


##


def test_default_does_not_cache_exceptions():
    n = 0

    @cached_function
    def f(v):
        nonlocal n
        n += 1
        raise v

    e = Err1()  # reuse one instance so the cache key is stable
    for i in range(3):
        with pytest.raises(Err1):
            f(e)
        assert n == i + 1  # recomputed every time


def test_caches_exact_and_subclass():
    n = 0

    @cached_function(cache_exceptions=(Err1,))
    def f(v):
        nonlocal n
        n += 1
        raise v

    e = Err1()
    for _ in range(3):
        with pytest.raises(Err1):
            f(e)
    assert n == 1  # exact match cached

    e2 = Err2()
    for _ in range(3):
        with pytest.raises(Err2):
            f(e2)
    assert n == 2  # subclass of Err1 cached too


def test_unlisted_exception_not_cached():
    n = 0

    @cached_function(cache_exceptions=(Err1,))
    def f(v):
        nonlocal n
        n += 1
        raise v

    e = Err3()
    for i in range(3):
        with pytest.raises(Err3):
            f(e)
        assert n == i + 1  # Err3 not a subclass of Err1 -> propagated, never cached


def test_single_type_not_tuple():
    n = 0

    @cached_function(cache_exceptions=Err1)
    def f():
        nonlocal n
        n += 1
        raise Err1

    for _ in range(3):
        with pytest.raises(Err1):
            f()
    assert n == 1


def test_cached_exception_is_same_instance():
    @cached_function(cache_exceptions=(ValueError,))
    def f():
        raise ValueError('boom')

    with pytest.raises(ValueError, match='boom') as ei1:
        f()
    with pytest.raises(ValueError, match='boom') as ei2:
        f()
    assert ei1.value is ei2.value  # the very same exception object is re-raised from cache


def test_success_and_exception_coexist():
    n = 0

    @cached_function(cache_exceptions=(Err1,))
    def f(x):
        nonlocal n
        n += 1
        if x < 0:
            raise Err1
        return x * 2

    assert f(3) == 6
    assert f(3) == 6
    assert n == 1
    with pytest.raises(Err1):
        f(-1)
    with pytest.raises(Err1):
        f(-1)
    assert n == 2
    assert f(3) == 6  # success entry untouched
    assert n == 2


##


def test_caches_base_exception():
    # KeyboardInterrupt is a BaseException but not an Exception - it must be allowed.
    n = 0

    @cached_function(cache_exceptions=(KeyboardInterrupt,))
    def f():
        nonlocal n
        n += 1
        raise KeyboardInterrupt

    for _ in range(2):
        with pytest.raises(KeyboardInterrupt):
            f()
    assert n == 1


def test_opts_validation_rejects_non_exception():
    # Validation happens when the decorator is actually applied to a function (the no-fn form just returns a partial).
    def f():
        return 1

    with pytest.raises(TypeError):
        cached_function(cache_exceptions=int)(f)
    with pytest.raises(TypeError):
        cached_function(cache_exceptions=(ValueError, int))(f)
    with pytest.raises(TypeError):
        cached_function(cache_exceptions='nope')(f)
