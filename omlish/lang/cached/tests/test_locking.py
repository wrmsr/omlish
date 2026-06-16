"""
Tests for cached_function locking. These are deterministic - the double-checked lock guarantees compute-once regardless
of scheduling, and a Barrier is used to maximize real contention without relying on sleeps.
"""
import dataclasses as dc
import threading

import pytest

from .... import testing as tu
from ..function import _CachedException
from ..function import cached_function


##


def test_lock_disabled_by_default():
    @cached_function
    def f():
        return 1

    assert f._lock is None  # type: ignore  # noqa


def test_lock_true_installs_lock():
    @cached_function(lock=True)
    def f():
        return 1

    assert f._lock is not None  # type: ignore  # noqa
    assert f() == 1


def test_lock_computes_once_under_contention():
    n_threads = 8
    n = 0
    barrier = threading.Barrier(n_threads)

    @cached_function(lock=True)
    def f(x):
        nonlocal n
        n += 1  # safe: executed under the cache lock
        return x * 2

    def do():
        barrier.wait()
        return f(10)

    results = tu.call_many_with_timeout([do] * n_threads)
    assert results == [20] * n_threads
    assert n == 1


def test_lock_distinct_keys_compute_independently():
    n = 0

    @cached_function(lock=True)
    def f(x):
        nonlocal n
        n += 1
        return x * 2

    assert f(1) == 2
    assert f(2) == 4
    assert f(1) == 2
    assert n == 2


@dc.dataclass()
class _LockErr(Exception):  # noqa
    pass


def test_lock_with_cache_exceptions_non_racing():
    n = 0

    @cached_function(lock=True, cache_exceptions=(_LockErr,))
    def f():
        nonlocal n
        n += 1
        raise _LockErr

    for _ in range(3):
        with pytest.raises(_LockErr):
            f()
    assert n == 1


class _RacyMap(dict):
    """
    Deterministically simulates a concurrent insert: the first lookup of a key (the pre-lock check) misses, the second
    (the in-lock recheck) returns a value as though another thread had stored it while we waited for the lock.
    """

    def __init__(self, injected):
        super().__init__()

        self._injected = injected
        self._n = 0

    def __getitem__(self, k):
        self._n += 1
        if self._n == 1:
            raise KeyError(k)
        return self._injected


def test_lock_cache_exceptions_in_lock_recheck_raises():
    # Regression: when a cached exception is stored by a racing thread, the thread that finds it on the in-lock recheck
    # must re-raise it, not return the internal _CachedException wrapper.
    injected = _CachedException(_LockErr())

    @cached_function(lock=True, cache_exceptions=(_LockErr,), map_maker=lambda: _RacyMap(injected))
    def f(x):
        raise AssertionError('value fn should not run - the in-lock recheck hits first')

    with pytest.raises(_LockErr):
        f(1)
