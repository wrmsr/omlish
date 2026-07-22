"""
Tests for the cache-key-maker, which canonicalizes a call's (*args, **kwargs) into a hashable tuple key honoring the
wrapped function's calling convention.
"""
import inspect

import pytest

from ..function import _make_cache_key_maker
from ..function import _nullary_cache_key_maker
from ..function import _self_cache_key_maker
from ..function import cached_function


##


def test_premade_nullary():
    assert _make_cache_key_maker(lambda: None) is _nullary_cache_key_maker
    assert _nullary_cache_key_maker() == ()


def test_premade_self():
    def f(self):
        pass

    assert _make_cache_key_maker(f) is _self_cache_key_maker
    assert _self_cache_key_maker(object()) is not None


def test_premade_self_ignores_annotations():
    def f(self: int):
        pass

    # strip_annotations means the annotated single-arg fn still matches the pre-made (self) key maker.
    assert _make_cache_key_maker(f) is _self_cache_key_maker


def test_non_self_single_arg_not_premade():
    km = _make_cache_key_maker(lambda x: None)
    assert km is not _self_cache_key_maker
    assert km(5) == (5,)


def test_bound_offset_drops_first():
    def f(self, x):
        pass

    km = _make_cache_key_maker(f, bound=True)
    assert km(7) == (7,)


def test_bound_self_only_is_nullary():
    def f(self):
        pass

    assert _make_cache_key_maker(f, bound=True) is _nullary_cache_key_maker


##


def test_positional_canonicalization():
    c = 0

    @cached_function
    def f(a, b):
        nonlocal c
        c += 1
        return a + b

    # All of these bind to the same (a, b) and must share one cache entry.
    assert f(1, 2) == 3
    assert f(a=1, b=2) == 3
    assert f(1, b=2) == 3
    assert f(b=2, a=1) == 3
    assert c == 1

    assert f(1, 3) == 4
    assert c == 2


def test_kwargs_catchall_sorted():
    km = _make_cache_key_maker(lambda **kw: None)
    assert km(x=1, y=2) == km(y=2, x=1)
    assert km(x=1, y=2) == ((('x', 1), ('y', 2)),)


def test_mixed_named_and_kwargs():
    km = _make_cache_key_maker(lambda a, **kw: None)
    assert km(1, z=2, y=3) == km(a=1, y=3, z=2)
    assert km(1) == (1, ())


##


def test_defaults_omitted_vs_explicit_distinct():
    # Matches stdlib lru_cache: passing a value equal to the default is NOT normalized to "omitted".
    c = 0

    @cached_function
    def f(a, b=10):
        nonlocal c
        c += 1
        return a + b

    assert f(1) == 11
    assert c == 1
    assert f(1) == 11  # omitted again -> hit
    assert c == 1
    assert f(1, 10) == 11  # explicit default -> distinct key -> miss
    assert c == 2
    assert f(1, b=10) == 11  # same as explicit -> hit
    assert c == 2


def test_defaults_omitted_is_stable():
    km = _make_cache_key_maker(lambda a, b=10: None)
    # The "omitted" key must be stable across calls (same sentinel object each time).
    assert km(1) == km(1)
    assert km(1) != km(1, 10)


##


def test_var_positional_distinct_by_args():
    c = 0

    @cached_function
    def f(*args):
        nonlocal c
        c += 1
        return sum(args)

    assert f(1, 2) == 3
    assert f(1, 2) == 3
    assert c == 1
    assert f(1, 2, 3) == 6
    assert c == 2
    assert f() == 0
    assert c == 3


def test_var_positional_with_kw_only():
    km = _make_cache_key_maker(lambda *args, k: None)
    assert str(inspect.signature(km)) == '(*args, k)'
    assert km(1, 2, k=3) == ((1, 2), 3)
    assert km(k=9) == ((), 9)


def test_defaulted_pk_before_var_positional():
    # Defaulted pos-or-kw params preceding *args are GENERAL-tier: the INLINE miss path would re-pass them by keyword,
    # colliding with re-passed varargs when they were filled positionally.
    c = 0

    @cached_function
    def f(a=1, *args):
        nonlocal c
        c += 1
        return (a, args)

    assert f(10, 20) == (10, (20,))
    assert f(10, 20) == (10, (20,))
    assert c == 1
    assert f() == (1, ())
    assert c == 2
    assert f(a=1) == (1, ())  # explicit default -> distinct key from omitted
    assert c == 3

    c = 0

    @cached_function
    def g(a, b=2, *args):
        nonlocal c
        c += 1
        return (a, b, args)

    assert g(1, 2, 3) == (1, 2, (3,))
    assert g(1, 2, 3) == (1, 2, (3,))
    assert c == 1
    assert g(1) == (1, 2, ())
    assert c == 2

    c = 0

    @cached_function
    def h(a=1, *args, **kw):
        nonlocal c
        c += 1
        return (a, args, kw)

    assert h(9, 8) == (9, (8,), {})
    assert h(9, 8, k=7) == (9, (8,), {'k': 7})
    assert h(9, 8) == (9, (8,), {})
    assert c == 2


##


def test_keymaker_enforces_kw_only():
    # The generated key maker reproduces the '*' separator, so passing a keyword-only arg positionally raises at the key
    # maker itself - early, and regardless of cache state.
    def g(a, b, *, c):
        return (a, b, c)

    km = _make_cache_key_maker(g)
    assert km(1, 2, c=3) == (1, 2, 3)
    assert km(1, b=2, c=3) == (1, 2, 3)  # still normalized to positional values
    with pytest.raises(TypeError):
        km(1, 2, 3)  # c is keyword-only

    @cached_function
    def cg(a, b, *, c):
        return (a, b, c)

    with pytest.raises(TypeError):
        cg(1, 2, 3)  # type: ignore


def test_keymaker_enforces_pos_only():
    # The '/' separator is reproduced, so a positional-only param passed by keyword raises at the key maker - and does
    # so even when a matching positive-key cache entry already exists (no silent warm-cache hit).
    @cached_function
    def f(x, /):
        return x

    assert f(5) == 5  # valid, warms key (5,)
    with pytest.raises(TypeError):
        f(x=5)  # type: ignore  # x is positional-only - must raise even though (5,) is cached

    km = _make_cache_key_maker(lambda x, /: None)
    assert km(5) == (5,)
    with pytest.raises(TypeError):
        km(x=5)


def test_keymaker_pos_only_at_end():
    # Regression for a trailing positional-only run (which lost its '/' before the with_seps fix).
    km = _make_cache_key_maker(lambda a, b, /: None)
    assert km(1, 2) == (1, 2)
    with pytest.raises(TypeError):
        km(1, b=2)  # b is positional-only


def test_keymaker_mixed_pos_and_kw_only_normalizes():
    @cached_function
    def f(a, /, b, *, c):
        return (a, b, c)

    # All valid forms normalize to the same key / single computation.
    assert f(1, 2, c=3) == (1, 2, 3)
    assert f(1, b=2, c=3) == (1, 2, 3)
    # invalid forms raise early
    with pytest.raises(TypeError):
        f(a=1, b=2, c=3)  # type: ignore  # a is positional-only
    with pytest.raises(TypeError):
        f(1, 2, 3)  # type: ignore  # c is keyword-only


##


def test_rejects_generator_function():
    def f():
        yield 1

    with pytest.raises(TypeError):
        cached_function(f)


def test_rejects_async_function():
    async def f():
        return 1

    with pytest.raises(TypeError):
        cached_function(f)
