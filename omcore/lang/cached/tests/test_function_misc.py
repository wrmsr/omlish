"""
Cross-cutting cached_function behaviors: wrapper-metadata / signature preservation, __bool__ guarding, decorator
stacking, static_init, and no_wrapper_update.
"""
import inspect

import pytest

from ...descriptors import unwrap_func
from ..function import cached_function
from ..function import static_init


##


def test_signature_preserved():
    def raw(a: int, b: str = 'x') -> tuple:
        return (a, b)

    f = cached_function(raw)
    assert inspect.signature(f) == inspect.signature(raw)


def test_wrapper_metadata_preserved():
    @cached_function
    def f(a, b):
        """my doc."""

        return a + b

    assert f.__name__ == 'f'
    assert f.__doc__ == 'my doc.'
    assert f.__wrapped__.__name__ == 'f'  # type: ignore
    assert inspect.unwrap(f) is f.__wrapped__  # type: ignore


def test_unwrap_func_reaches_original():
    def raw(x):
        return x

    f = cached_function(raw)
    assert unwrap_func(f) is raw


def test_method_signature_includes_self():
    # The bound wrapper's __wrapped__ is the unbound function, so its reflected signature keeps `self`.
    class C:
        @cached_function
        def m(self, x: int) -> int:
            return x

    assert str(inspect.signature(C.m)) == '(self, x: int) -> int'
    assert str(inspect.signature(C().m)) == '(self, x: int) -> int'


##


def test_bool_raises():
    @cached_function
    def f():
        return 1

    with pytest.raises(TypeError):
        bool(f)  # truthiness checks (e.g. `if f:`) all route through this guard


##


def test_double_wrap():
    n = 0

    def raw(x):
        nonlocal n
        n += 1
        return x + 1

    f = cached_function(cached_function(raw))
    assert f(1) == 2
    assert f(1) == 2
    assert n == 1
    assert unwrap_func(f) is raw


##


def test_no_wrapper_update_skips_metadata():
    @cached_function(no_wrapper_update=True)
    def f(a, b):
        return a + b

    assert f(1, 2) == 3
    assert not hasattr(f, '__wrapped__')
    assert not hasattr(f, '__name__')


##


def test_static_init_runs_immediately_and_caches():
    log = []

    @static_init
    def si():
        log.append(1)
        return 'v'

    assert log == [1]  # ran at decoration time
    assert si() == 'v'
    assert si() == 'v'
    assert log == [1]  # cached -> no further runs


def test_reset_returns_none():
    @cached_function
    def f():
        return 1

    assert f() == 1
    assert f.reset() is None  # type: ignore
