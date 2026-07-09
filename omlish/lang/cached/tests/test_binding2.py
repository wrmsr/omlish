"""
The contract suite for the species-based cached_function rewrite (function2): descriptor-protocol behavior, key making,
exception caching, locking, storage, pickling, metadata, unbound-call reconciliation, __set_name__, codegen internals,
and an axis-interaction matrix.
"""
import collections
import dataclasses as dc
import functools
import inspect
import linecache
import pickle
import threading

import pytest

from .... import testing as tu
from ...contextmanagers import context_wrapped
from ...descriptors import unwrap_func
from ..function2 import _MISSING
from ..function2 import _BoundCachedFunction
from ..function2 import _CachedException
from ..function2 import _DescriptorCachedFunction
from ..function2 import _FreeCachedFunction
from ..function2 import _make_cache_key_maker
from ..function2 import _nullary_cache_key_maker
from ..function2 import _self_cache_key_maker
from ..function2 import _UnboundCachedMethod
from ..function2 import cached_function
from ..function2 import static_init


##
# Instance binding & descriptor protocol


def test_instance_binding_caches_in_instance_dict():
    class C:
        def __init__(self, v):
            self.v = v

        @cached_function
        def m(self):
            return ('m', self.v)

    c = C(1)
    assert 'm' not in c.__dict__
    b1 = c.m
    assert 'm' in c.__dict__  # bound wrapper memoized on the instance
    b2 = c.m
    assert b1 is b2  # subsequent access returns the memoized bound wrapper (no rebind)
    assert isinstance(b1, _BoundCachedFunction)  # lightweight per-instance wrapper
    assert isinstance(C.__dict__['m'], _DescriptorCachedFunction)  # the descriptor itself


def test_per_instance_cache_isolation():
    n = 0

    class C:
        def __init__(self, v):
            self.v = v

        @cached_function
        def m(self):
            nonlocal n
            n += 1
            return ('m', self.v)

    c1 = C(1)
    c2 = C(2)
    for _ in range(2):
        assert c1.m() == ('m', 1)
    assert n == 1
    for _ in range(2):
        assert c2.m() == ('m', 2)
    assert n == 2
    # distinct instances -> distinct wrappers and storage (nullary methods store in the per-wrapper slot)
    assert c1.m is not c2.m
    assert c1.m._v == ('m', 1)  # type: ignore  # noqa
    assert c2.m._v == ('m', 2)  # type: ignore  # noqa


def test_per_instance_cache_isolation_general():
    n = 0

    class C:
        def __init__(self, v):
            self.v = v

        @cached_function
        def m(self, x):
            nonlocal n
            n += 1
            return (self.v, x)

    c1 = C(1)
    c2 = C(2)
    for _ in range(2):
        assert c1.m(5) == (1, 5)
    assert n == 1
    for _ in range(2):
        assert c2.m(5) == (2, 5)
    assert n == 2
    assert c1.m._values is not c2.m._values  # type: ignore  # noqa
    assert c1.m._values == {(5,): (1, 5)}  # type: ignore  # noqa  # self is clipped - never a key component


def test_descriptor_and_bound_have_distinct_storage():
    class C:
        @cached_function
        def m(self):
            return 1

    c = C()
    desc = C.__dict__['m']
    bound = c.m
    assert bound() == 1
    assert bound._v == 1  # type: ignore  # noqa
    assert desc._v is _MISSING  # noqa  # the descriptor's own direct-call cache is untouched


def test_inherited_method_binds_on_subclass_instance():
    n = 0

    class A:
        @cached_function
        def m(self):
            nonlocal n
            n += 1
            return type(self).__name__

    class B(A):
        pass

    b = B()
    for _ in range(2):
        assert b.m() == 'B'
    assert n == 1
    assert 'm' in b.__dict__


def test_no_shared_instance_refs():
    # The headline difference from functools.cached*: caching never hard-refs an instance from any shared store. All
    # per-instance state lives on the instance itself (a collectable self-cycle), so instances die normally.
    import gc
    import weakref

    class C:
        @cached_function
        def m(self):
            return ('m', id(self))

    c1 = C()
    c1.m()
    c2 = C()
    C.m(c2)  # the unbound reconciliation path must not retain instances either
    r1 = weakref.ref(c1)
    r2 = weakref.ref(c2)
    del c1
    del c2
    gc.collect()
    assert r1() is None
    assert r2() is None


##
# Classmethods


def test_classmethod_owner_caching_and_subclass_distinctness():
    calls = []

    class K:
        cv = 'K'

        @cached_function
        @classmethod
        def cm(cls):
            calls.append(cls.__name__)
            return cls.cv

    class L(K):
        cv = 'L'

    for _ in range(2):
        assert K.cm() == 'K'
    assert calls == ['K']  # cached on owner K
    # owner-bound wrapper installed on the class itself
    assert isinstance(K.__dict__['cm'], _BoundCachedFunction)

    for _ in range(2):
        assert L.cm() == 'L'  # subclass recomputes against its own owner
    assert calls == ['K', 'L']
    assert isinstance(L.__dict__['cm'], _BoundCachedFunction)


def test_classmethod_subclass_access_before_parent():
    calls = []

    class K:
        cv = 'K'

        @cached_function
        @classmethod
        def cm(cls):
            calls.append(cls.__name__)
            return cls.cv

    class L(K):
        cv = 'L'

    for _ in range(2):
        assert L.cm() == 'L'
    assert calls == ['L']
    for _ in range(2):
        assert K.cm() == 'K'
    assert calls == ['L', 'K']


def test_classmethod_instance_access_shares_class_cache():
    calls = []

    class K:
        cv = 'K'

        @cached_function
        @classmethod
        def cm(cls):
            calls.append(cls.__name__)
            return cls.cv

    for _ in range(2):
        assert K.cm() == 'K'
    assert calls == ['K']
    for _ in range(2):
        assert K().cm() == 'K'  # instance access of a classmethod hits the class cache
    assert calls == ['K']


def test_classmethod_with_args():
    calls = []

    class K:
        @cached_function
        @classmethod
        def cm(cls, x):
            calls.append((cls.__name__, x))
            return (cls.__name__, x)

    for _ in range(2):
        assert K.cm(1) == ('K', 1)
        assert K.cm(x=1) == ('K', 1)  # canonicalized to the same key
    assert calls == [('K', 1)]
    assert K.cm(2) == ('K', 2)
    assert calls == [('K', 1), ('K', 2)]


def test_classmethod_reset():
    n = 0

    class K:
        @cached_function
        @classmethod
        def cm(cls):
            nonlocal n
            n += 1
            return n

    assert K.cm() == 1
    assert K.cm() == 1
    K.cm.reset()  # type: ignore
    assert K.cm() == 2


##
# Staticmethods


def test_staticmethod():
    n = 0

    class C:
        @cached_function
        @staticmethod
        def s(x):
            nonlocal n
            n += 1
            return x * 2

    for _ in range(2):
        assert C.s(3) == 6
        assert C().s(3) == 6
    assert n == 1
    for _ in range(2):
        assert C.s(4) == 8
    assert n == 2
    # staticmethod wrapping yields a shared (free) cached function, not a per-instance descriptor
    assert isinstance(C.__dict__['s'], _FreeCachedFunction)


def test_staticmethod_nullary():
    n = 0

    class C:
        @cached_function
        @staticmethod
        def s():
            nonlocal n
            n += 1
            return 'C.s'

    class D(C):
        pass

    for o in [C, D, C(), D()]:
        assert o.s() == 'C.s'  # type: ignore
    assert n == 1


##
# Free / runtime-bound


def test_runtime_bound_method():
    class Foo:
        def __init__(self):
            self.c = 0

        def f(self, x):
            self.c += 1
            return x + 1

    foo = Foo()
    f = cached_function(foo.f)
    assert isinstance(f, _FreeCachedFunction)
    for _ in range(2):
        assert f(5) == 6
    assert foo.c == 1
    for _ in range(2):
        assert f(6) == 7
    assert foo.c == 2


def test_runtime_bound_method_nullary():
    class Foo:
        def __init__(self):
            self.c = 0

        def f(self):
            self.c += 1
            return 42

    foo = Foo()
    f = cached_function(foo.f)
    for _ in range(2):
        assert f() == 42
    assert foo.c == 1
    assert f._values is None  # type: ignore  # noqa  # nullary species: single-slot storage, no map
    assert f._v == 42  # type: ignore  # noqa


def test_free_function():
    c = 0

    @cached_function
    def f(x, y):
        nonlocal c
        c += 1
        return x + y

    for _ in range(2):
        assert f(1, 2) == 3
        assert c == 1


def test_free_nullary():
    c = 0

    @cached_function
    def f():
        nonlocal c
        c += 1
        return 'f'

    for _ in range(2):
        assert f() == 'f'
    assert c == 1
    f.reset()  # type: ignore
    for _ in range(2):
        assert f() == 'f'
    assert c == 2


def test_nullary_rejects_args():
    @cached_function
    def f():
        return 1

    assert f() == 1
    with pytest.raises(TypeError):
        f(1)  # type: ignore
    with pytest.raises(TypeError):
        f(x=1)  # type: ignore


##
# Custom __get__ honoring


def test_custom_get_is_honored():
    # cached_function over a descriptor with its own __get__ must call through that __get__ on bind.
    class CountingDescriptor:
        def __init__(self, fn):
            self._fn = fn
            self.get_count = 0
            functools.update_wrapper(self, fn)  # type: ignore

        def __get__(self, instance, owner=None):
            self.get_count += 1
            return self._fn.__get__(instance, owner)

    def m(self):
        return ('m', self.v)

    cd = CountingDescriptor(m)

    class C:
        def __init__(self, v):
            self.v = v

        m = cached_function(cd)  # type: ignore

    assert cd.get_count == 0
    c = C(7)
    for _ in range(2):
        assert c.m() == ('m', 7)
    assert cd.get_count == 1  # bound exactly once for this instance
    for _ in range(2):
        assert c.m() == ('m', 7)
    assert cd.get_count == 1  # memoized bound wrapper -> no further __get__


##
# Unbound A.f(inst) reconciliation


def test_unbound_call_via_class_routes_to_instance_cache():
    # A.f(inst) routes to inst's own per-instance cache (inst clipped off, never keyed), sharing the exact wrapper and
    # store that inst.f() uses - no shared/global store, no self in the key.
    n = 0

    class C:
        def __init__(self, v):
            self.v = v

        @cached_function
        def m(self):
            nonlocal n
            n += 1
            return ('m', self.v)

    c = C(1)
    for _ in range(2):
        assert C.m(c) == ('m', 1)  # unbound call through the class
    assert n == 1
    for _ in range(2):
        assert c.m() == ('m', 1)  # ... shares the same cached value
    assert n == 1
    assert 'm' in c.__dict__  # stored on the instance, not on the descriptor
    assert c.m is c.__dict__['m']

    c2 = C(2)
    for _ in range(2):
        assert C.m(c2) == ('m', 2)  # distinct instance -> distinct cache
    assert n == 2


def test_unbound_call_general_shares_key_space():
    n = 0

    class C:
        @cached_function
        def m(self, x):
            nonlocal n
            n += 1
            return x * 2

    c = C()
    assert c.m(3) == 6
    assert C.m(c, 3) == 6  # same key as the bound call - self never keyed
    assert C.m(c, x=3) == 6  # canonicalized
    assert n == 1


def test_unbound_is_per_descriptor_singleton():
    class C:
        @cached_function
        def m(self):
            return 1

    u = C.m
    assert u is C.m
    assert isinstance(u, _UnboundCachedMethod)

    class D(C):
        pass

    assert D.m is u  # unoverridden subclass access reaches the same singleton


def test_unbound_call_with_subclass_override_does_not_clobber():
    n_a = 0
    n_b = 0

    class A:
        @cached_function
        def m(self):
            nonlocal n_a
            n_a += 1
            return 'A'

    class B(A):
        @cached_function
        def m(self):
            nonlocal n_b
            n_b += 1
            return 'B'

    # Pre-access: A.m(b) must not install anything under 'm' - B's override owns that name.
    b = B()
    for _ in range(2):
        assert A.m(b) == 'A'
    assert n_a == 2  # correct-but-uncached escape hatch
    assert 'm' not in b.__dict__

    for _ in range(2):
        assert b.m() == 'B'
    assert n_b == 1

    # Post-access: A.m(b) must not clobber b's installed override wrapper.
    assert A.m(b) == 'A'
    assert b.m() == 'B'
    assert n_b == 1
    assert b.__dict__['m']._desc is B.__dict__['m']  # noqa


def test_unbound_call_with_manual_instance_attr_does_not_clobber():
    class C:
        def __init__(self, v):
            self.v = v

        @cached_function
        def m(self):
            return ('m', self.v)

    c = C(9)
    c.m = 5  # type: ignore  # non-data descriptor - instance attr wins for c.m
    assert C.m(c) == ('m', 9)  # python semantics: calls C's fn with self=c
    assert c.m == 5  # untouched


def test_unbound_kwargs_and_convention_enforcement():
    class C:
        @cached_function
        def m(self, a, *, b):
            return (a, b)

    c = C()
    assert C.m(c, 1, b=2) == (1, 2)
    with pytest.raises(TypeError):
        C.m(c, 1, 2)  # type: ignore  # b is keyword-only
    with pytest.raises(TypeError):
        C.m()  # type: ignore  # missing the instance


def test_slotted_instances_raise():
    class S:
        __slots__ = ()

        @cached_function
        def m(self):
            return 1

    with pytest.raises(AttributeError):
        S().m  # noqa
    with pytest.raises(AttributeError):
        S.m(S())


##
# __set_name__


def test_set_name_adopts_attribute_name():
    n = 0

    def _impl(self):
        nonlocal n
        n += 1
        return n

    class C:
        foo = cached_function(_impl)

    c = C()
    assert c.foo() == 1
    assert c.foo() == 1  # cached - the wrapper installs under 'foo', the actual attribute name
    assert 'foo' in c.__dict__
    assert '_impl' not in c.__dict__


def test_set_name_rejects_two_names():
    def _impl(self):
        return 1

    one = cached_function(_impl)

    with pytest.raises(TypeError):
        class C:  # noqa
            a = one
            b = one


def test_set_name_same_name_two_classes_ok():
    n = 0

    def _impl(self):
        nonlocal n
        n += 1
        return n

    shared = cached_function(_impl)

    class A:
        m = shared

    class B:
        m = shared

    assert A().m() == 1
    assert B().m() == 2  # distinct instances -> distinct caches, shared descriptor is fine


##
# Key making


def test_premade_nullary():
    assert _make_cache_key_maker(lambda: None) is _nullary_cache_key_maker
    assert _nullary_cache_key_maker() == ()


def test_premade_self():
    def f(self):
        pass

    assert _make_cache_key_maker(f) is _self_cache_key_maker
    assert _make_cache_key_maker(f, bound=True) is _nullary_cache_key_maker


def test_premade_self_ignores_annotations():
    def f(self: int):
        pass

    # strip_annotations means the annotated single-arg fn still matches the pre-made (self) key maker.
    assert _make_cache_key_maker(f) is _self_cache_key_maker


def test_bound_offset_drops_first():
    def f(self, x):
        pass

    km = _make_cache_key_maker(f, bound=True)
    assert km(7) == (7,)


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


def test_func_only_kws():
    c = 0

    @cached_function
    def foo(**kw):
        nonlocal c
        c += 1
        return kw

    for _ in range(2):
        assert foo() == {}
        assert c == 1

    for _ in range(2):
        assert foo(x=1) == {'x': 1}
        assert c == 2

    for _ in range(2):
        assert foo(x=1, y=2) == {'x': 1, 'y': 2}
        assert c == 3
        assert foo(y=2, x=1) == {'x': 1, 'y': 2}
        assert c == 3


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


def test_var_positional():
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


def test_keymaker_enforces_kw_only():
    # The generated key maker reproduces the '*' separator, so passing a keyword-only arg positionally raises at the
    # key maker itself - early, and regardless of cache state.
    @cached_function
    def cg(a, b, *, c):
        return (a, b, c)

    assert cg(1, 2, c=3) == (1, 2, 3)
    assert cg(1, b=2, c=3) == (1, 2, 3)  # still normalized to positional values
    with pytest.raises(TypeError):
        cg(1, 2, 3)  # type: ignore  # c is keyword-only - raises even with a warm cache


def test_keymaker_enforces_pos_only():
    # The '/' separator is reproduced, so a positional-only param passed by keyword raises at the key maker - and does
    # so even when a matching positive-key cache entry already exists (no silent warm-cache hit).
    @cached_function
    def f(x, /):
        return x

    assert f(5) == 5  # valid, warms key (5,)
    with pytest.raises(TypeError):
        f(x=5)  # type: ignore  # x is positional-only - must raise even though (5,) is cached

    km = _make_cache_key_maker(lambda a, b, /: None)
    assert km(1, 2) == (1, 2)
    with pytest.raises(TypeError):
        km(1, b=2)  # b is positional-only (trailing '/' regression)


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


def test_partials():
    c = 0

    @cached_function
    def f(x):
        nonlocal c
        c += 1
        return x + 1

    pf = functools.partial(f, 1)
    assert c == 0
    for _ in range(2):
        assert pf() == 2
        assert f(1) == 2
        assert c == 1


def test_partial_fn_wrapped():
    c = 0

    def f(x, y):
        nonlocal c
        c += 1
        return (x, y)

    pf = cached_function(functools.partial(f, 1))
    for _ in range(2):
        assert pf(2) == (1, 2)
    assert c == 1
    assert pf(3) == (1, 3)
    assert c == 2


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


##
# Exception caching


class Err1(Exception):  # noqa
    pass


class Err2(Err1):  # noqa
    pass


class Err3(Exception):  # noqa
    pass


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


def test_cached_keyerror_is_cache_hit():
    # Regression: a cached KeyError must re-raise as a hit, not be swallowed by the cache probe's own KeyError handling
    # and recomputed forever.
    n = 0

    @cached_function(cache_exceptions=(KeyError,))
    def f(x):
        nonlocal n
        n += 1
        raise KeyError(x)

    for _ in range(3):
        with pytest.raises(KeyError):
            f(1)
    assert n == 1


def test_cached_keyerror_is_cache_hit_locked():
    n = 0

    @cached_function(lock=True, cache_exceptions=(KeyError,))
    def f(x):
        nonlocal n
        n += 1
        raise KeyError(x)

    for _ in range(3):
        with pytest.raises(KeyError):
            f(1)
    assert n == 1


def test_cached_exception_nullary():
    n = 0

    @cached_function(cache_exceptions=(Err1,))
    def f():
        nonlocal n
        n += 1
        raise Err1

    for _ in range(3):
        with pytest.raises(Err1):
            f()
    assert n == 1
    f.reset()  # type: ignore
    with pytest.raises(Err1):
        f()
    assert n == 2


def test_cached_exception_method():
    n = 0

    class C:
        @cached_function(cache_exceptions=(Err1,))
        def m(self):
            nonlocal n
            n += 1
            raise Err1

    c = C()
    for _ in range(3):
        with pytest.raises(Err1):
            c.m()
    assert n == 1
    c2 = C()
    with pytest.raises(Err1):
        c2.m()
    assert n == 2  # per-instance caches


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


##
# Locking


@dc.dataclass()
class _LockErr(Exception):  # noqa
    pass


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


def test_lock_false_is_no_lock():
    @cached_function(lock=False)
    def f():
        return 1

    assert f._lock is None  # type: ignore  # noqa
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


def test_lock_computes_once_under_contention_nullary():
    n_threads = 8
    n = 0
    barrier = threading.Barrier(n_threads)

    @cached_function(lock=True)
    def f():
        nonlocal n
        n += 1
        return 'v'

    def do():
        barrier.wait()
        return f()

    results = tu.call_many_with_timeout([do] * n_threads)
    assert results == ['v'] * n_threads
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


def test_lock_per_instance():
    class C:
        @cached_function(lock=True)
        def m(self):
            return 1

    c1 = C()
    c2 = C()
    assert c1.m() == 1
    assert c2.m() == 1
    assert c1.m._lock is not c2.m._lock  # type: ignore  # noqa  # lock=True yields a fresh lock per bound instance


def test_lock_held_around_compute():
    events = []

    class _EventLock:
        def __enter__(self):
            events.append('enter')

        def __exit__(self, exc_type, exc_val, exc_tb):
            events.append('exit')

    @cached_function(lock=_EventLock())
    def f():
        events.append('compute')
        return 1

    assert f() == 1
    assert events == ['enter', 'compute', 'exit']
    assert f() == 1
    assert events == ['enter', 'compute', 'exit']  # hits skip the lock entirely


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


def test_lock_recheck_returns_injected_value():
    @cached_function(lock=True, map_maker=lambda: _RacyMap('won'))
    def f(x):
        raise AssertionError('value fn should not run - the in-lock recheck hits first')

    assert f(1) == 'won'


def test_lock_recheck_raises_injected_cached_exception():
    # Regression: when a cached exception is stored by a racing thread, the thread that finds it on the in-lock recheck
    # must re-raise it, not return the internal _CachedException wrapper.
    injected = _CachedException(_LockErr())

    @cached_function(lock=True, cache_exceptions=(_LockErr,), map_maker=lambda: _RacyMap(injected))
    def f(x):
        raise AssertionError('value fn should not run - the in-lock recheck hits first')

    with pytest.raises(_LockErr):
        f(1)


class _InjectingLock:
    """
    Deterministically simulates a racing thread for nullary species: __enter__ fires a callback that stores into
    the slot, as though another thread computed while we waited for the lock.
    """

    def __init__(self):
        super().__init__()

        self.on_enter = None

    def __enter__(self):
        if (cb := self.on_enter) is not None:
            self.on_enter = None
            cb()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_lock_nullary_recheck_returns_injected_value():
    lk = _InjectingLock()

    @cached_function(lock=lk)
    def f():
        raise AssertionError('value fn should not run - the in-lock recheck hits first')

    lk.on_enter = lambda: setattr(f, '_v', 'won')
    assert f() == 'won'


def test_lock_nullary_recheck_raises_injected_cached_exception():
    lk = _InjectingLock()

    @cached_function(lock=lk, cache_exceptions=(_LockErr,))
    def f():
        raise AssertionError('value fn should not run - the in-lock recheck hits first')

    lk.on_enter = lambda: setattr(f, '_v', _CachedException(_LockErr()))
    with pytest.raises(_LockErr):
        f()


##
# Storage & maps


def test_nullary_storage_contract():
    @cached_function
    def f():
        return 1

    assert f._values is None  # type: ignore  # noqa  # nullary species: no backing map at all
    assert f._v is _MISSING  # type: ignore  # noqa
    assert f() == 1
    assert f._v == 1  # type: ignore  # noqa


def test_general_storage_contract():
    @cached_function
    def f(x):
        return x

    assert type(f._values) is dict  # type: ignore  # noqa
    assert f(1) == 1
    assert f._values == {(1,): 1}  # type: ignore  # noqa


def test_custom_map_maker():
    @cached_function(map_maker=collections.OrderedDict)
    def f(x):
        return x

    assert f(1) == 1
    assert isinstance(f._values, collections.OrderedDict)  # type: ignore  # noqa
    assert dict(f._values) == {(1,): 1}  # type: ignore  # noqa


def test_custom_map_maker_forces_map_for_nullary_signature():
    # A non-dict map maker must be honored even for a nullary signature (its entries may be observed / evicted), so the
    # single-slot specialization is skipped.
    @cached_function(map_maker=collections.OrderedDict)
    def f():
        return 'v'

    assert f() == 'v'
    assert isinstance(f._values, collections.OrderedDict)  # type: ignore  # noqa
    assert dict(f._values) == {(): 'v'}  # type: ignore  # noqa
    assert f._v is _MISSING  # type: ignore  # noqa


def test_none_is_cached():
    n = 0

    @cached_function
    def f(x):
        nonlocal n
        n += 1
        return None  # noqa

    assert f(1) is None
    assert f(1) is None
    assert n == 1


def test_reset_recomputes():
    n = 0

    @cached_function
    def f(x):
        nonlocal n
        n += 1
        return n

    assert f(1) == 1
    assert f(1) == 1
    assert f.reset() is None  # type: ignore
    assert f(1) == 2
    assert f(1) == 2


def test_reset_preserves_map_type():
    # Regression: reset() must rebuild the backing map via map_maker, not replace it with a bare dict.
    @cached_function(map_maker=collections.OrderedDict)
    def f(x):
        return x

    assert f(1) == 1
    f.reset()  # type: ignore
    assert isinstance(f._values, collections.OrderedDict)  # type: ignore  # noqa
    assert f(2) == 2
    assert dict(f._values) == {(2,): 2}  # type: ignore  # noqa


def test_bound_reset():
    n = 0

    class C:
        @cached_function
        def m(self):
            nonlocal n
            n += 1
            return n

    c = C()
    assert c.m() == 1
    assert c.m() == 1
    c.m.reset()  # type: ignore
    assert c.m() == 2

    c2 = C()
    assert c2.m() == 3
    c.m.reset()  # type: ignore
    assert c2.m() == 3  # other instances' caches unaffected


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


##
# Pickling


class _PickleTestClass:
    _c = 0

    @classmethod
    def c(cls) -> int:
        c = cls._c
        cls._c += 1
        return c

    @cached_function()
    def d_func(self) -> int:
        return self.c()

    @cached_function(transient=True)
    def t_func(self) -> int:
        return self.c()

    @cached_function()
    def g_func(self, x) -> tuple:
        return (x, self.c())


class _PickleTestClass2(_PickleTestClass):
    _c = 0


def test_pickling():
    for c in [
        _PickleTestClass(),
        _PickleTestClass2(),
    ]:
        for _ in range(2):
            assert c.d_func() == 0
            assert c.t_func() == 1
            assert c.g_func(9) == (9, 2)

        c2 = pickle.loads(pickle.dumps(c))  # noqa
        assert type(c2) is type(c)

        for _ in range(2):
            assert c2.d_func() == 0  # non-transient nullary (slot) cache survived
            assert c2.t_func() == 3  # transient cache reset -> recomputed
            assert c2.g_func(9) == (9, 2)  # non-transient map cache survived


class _NoAccessPickleClass:
    @cached_function()
    def f(self) -> int:
        return 42


def test_pickling_without_prior_access():
    # An instance whose cached method was never accessed has no bound wrapper in its __dict__; it should pickle cleanly
    # and rebind fresh on the other side.
    c = _NoAccessPickleClass()
    c2 = pickle.loads(pickle.dumps(c))  # noqa
    assert c2.f() == 42
    assert c2.f() == 42


class _FreeHolder:
    def __init__(self):
        self.calls = 0

    def m(self, x):
        self.calls += 1
        return x + 1

    def n(self):
        self.calls += 1
        return 42


def test_free_bound_method_pickling():
    h = _FreeHolder()
    cf = cached_function(h.m)
    assert cf(5) == 6
    assert cf(5) == 6
    assert h.calls == 1

    cf2 = pickle.loads(pickle.dumps(cf))  # noqa
    assert dict(cf2._values) == {(5,): 6}  # noqa  # non-transient cache survived the round trip
    assert cf2(5) == 6
    assert cf2(6) == 7


def test_free_bound_method_transient_pickling():
    h = _FreeHolder()
    cf = cached_function(h.m, transient=True)
    assert cf(5) == 6
    assert dict(cf._values) == {(5,): 6}  # type: ignore  # noqa

    cf2 = pickle.loads(pickle.dumps(cf))  # noqa
    assert dict(cf2._values) == {}  # noqa  # transient cache dropped on pickle
    assert cf2(5) == 6  # recomputed fresh


def test_free_nullary_pickling():
    # Regression: the nullary species stores in the single slot, which must survive pickling like the map does.
    h = _FreeHolder()
    cf = cached_function(h.n)
    assert cf() == 42
    assert h.calls == 1

    cf2 = pickle.loads(pickle.dumps(cf))  # noqa
    assert cf2._v == 42  # noqa  # slot survived
    h2 = cf2._value_fn.__self__  # noqa
    assert cf2() == 42
    assert h2.calls == 1  # not recomputed


def test_free_nullary_transient_pickling():
    h = _FreeHolder()
    cf = cached_function(h.n, transient=True)
    assert cf() == 42

    cf2 = pickle.loads(pickle.dumps(cf))  # noqa
    assert cf2._v is _MISSING  # noqa
    h2 = cf2._value_fn.__self__  # noqa
    assert cf2() == 42
    assert h2.calls == 2  # recomputed fresh


@cached_function
def _module_level_cached_fn(x):
    return x + 1


def test_module_level_function_pickles_by_reference():
    # Like plain functions (and functools.lru_cache wrappers), module-level cached functions pickle by reference: the
    # unpickled result is whatever the qualname resolves to, cache state and all.
    assert _module_level_cached_fn(1) == 2
    cf2 = pickle.loads(pickle.dumps(_module_level_cached_fn))  # noqa
    assert cf2 is _module_level_cached_fn


def test_local_function_pickling_fails_loudly():
    @cached_function
    def f(x):
        return x

    with pytest.raises(pickle.PicklingError):
        pickle.dumps(f)  # <locals> qualname cannot resolve


class _ExcPickleClass:
    n_computes = 0

    @cached_function(cache_exceptions=(RuntimeError,))
    def f(self) -> None:
        type(self).n_computes += 1
        raise RuntimeError('boom')


def test_cached_exception_pickling():
    c = _ExcPickleClass()
    with pytest.raises(RuntimeError, match='boom'):
        c.f()
    assert _ExcPickleClass.n_computes == 1

    c2 = pickle.loads(pickle.dumps(c))  # noqa
    with pytest.raises(RuntimeError, match='boom'):
        c2.f()
    assert _ExcPickleClass.n_computes == 1  # re-raised from the pickled cache, not recomputed


def _renamed_pickle_impl(self):
    return 7


class _RenamedPickleClass:
    foo = cached_function(_renamed_pickle_impl)


def test_renamed_attr_pickling():
    c = _RenamedPickleClass()
    assert c.foo() == 7
    assert 'foo' in c.__dict__
    c2 = pickle.loads(pickle.dumps(c))  # noqa
    assert c2.foo() == 7


class _UnpicklableBitsClass:
    @cached_function
    def m(self) -> int:
        return 1

    @cached_function
    @classmethod
    def cm(cls) -> int:
        return 2


def test_unpicklable_wrappers_raise_cleanly():
    # The raw in-class descriptor is shadowed by __get__ on qualname resolution and must fail loudly.
    with pytest.raises(pickle.PicklingError):
        pickle.dumps(_UnpicklableBitsClass.__dict__['m'])

    assert _UnpicklableBitsClass.cm() == 2
    with pytest.raises(TypeError):
        pickle.dumps(_UnpicklableBitsClass.__dict__['cm'])  # the owner-installed classmethod-scope wrapper


def test_unbound_method_pickles_by_reference():
    u = _UnpicklableBitsClass.m
    u2 = pickle.loads(pickle.dumps(u))  # noqa
    assert u2 is u  # the per-descriptor singleton, resolved by qualname


##
# Metadata & misc


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


def test_bound_wrapper_metadata():
    class C:
        @cached_function
        def m(self, x: int) -> int:
            """m doc."""

            return x

    c = C()
    b = c.m
    assert b.__name__ == 'm'
    assert b.__doc__ == 'm doc.'
    assert b.__wrapped__ is inspect.unwrap(b)  # type: ignore


def test_method_signature_includes_self():
    # Wrappers' __wrapped__ is the unbound function, so their reflected signature keeps `self` - on the unbound method
    # and on bound wrappers alike.
    class C:
        @cached_function
        def m(self, x: int) -> int:
            return x

    assert str(inspect.signature(C.m)) == '(self, x: int) -> int'
    assert str(inspect.signature(C().m)) == '(self, x: int) -> int'


def test_unwrap_func_reaches_original():
    def raw(x):
        return x

    f = cached_function(raw)
    assert unwrap_func(f) is raw

    class C:
        m = cached_function(raw)

    assert unwrap_func(C.m) is raw
    assert unwrap_func(C().m) is raw


def test_bool_raises_everywhere():
    @cached_function
    def f():
        return 1

    class C:
        @cached_function
        def m(self):
            return 1

        @cached_function
        @classmethod
        def cm(cls):
            return 2

    c = C()
    assert C.cm() == 2
    for obj in [f, C.__dict__['m'], C.m, c.m, C.__dict__['cm']]:
        with pytest.raises(TypeError):
            bool(obj)  # truthiness checks (e.g. `if f:`) all route through this guard


def test_double_wrap():
    n = 0

    def raw(x):
        nonlocal n
        n += 1
        return x + 1

    inner = cached_function(raw)
    outer = cached_function(inner)
    assert outer(1) == 2
    assert outer(1) == 2
    assert n == 1
    assert unwrap_func(outer) is raw


def test_double_wrap_state_not_clobbered():
    # Metadata is copied before own state is set, so wrapping another cached function can't leak the inner wrapper's
    # state (values/opts/value_fn) into the outer via the __dict__ copy.
    def raw(x):
        return x + 1

    inner = cached_function(raw)
    outer = cached_function(inner)
    assert outer._values is not inner._values  # type: ignore  # noqa
    assert outer._value_fn is inner  # type: ignore  # noqa
    assert outer(1) == 2
    assert dict(outer._values) == {(1,): 2}  # type: ignore  # noqa
    assert dict(inner._values) == {(1,): 2}  # noqa


def test_no_wrapper_update_skips_metadata():
    @cached_function(no_wrapper_update=True)
    def f(a, b):
        return a + b

    assert f(1, 2) == 3
    assert not hasattr(f, '__wrapped__')
    assert not hasattr(f, '__name__')


def test_no_wrapper_update_bound():
    class C:
        @cached_function(no_wrapper_update=True)
        def m(self):
            return 1

    c = C()
    assert c.m() == 1
    assert not hasattr(c.m, '__wrapped__')


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


def test_context_wrapped():
    class ContextCounter:
        enter_count = 0
        exit_count = 0

        def __enter__(self):
            self.enter_count += 1

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.exit_count += 1

    class C:
        def __init__(self) -> None:
            super().__init__()
            self._lock = ContextCounter()

        @cached_function
        @context_wrapped('_lock')
        def a(self):
            return 'a'

        @cached_function
        @context_wrapped('_lock')
        def b(self):
            return f'b{self.a()}'

        @cached_function
        @context_wrapped('_lock')
        def c(self):
            return f'c{self.a()}'

        @cached_function
        @context_wrapped('_lock')
        def d(self):
            return f'd{self.c()}{self.b()}'

    c = C()
    assert c.d() == 'dcaba'
    assert c._lock.enter_count == 4  # noqa
    assert c._lock.exit_count == 4  # noqa


##
# Species & codegen internals


def test_species_classes_are_shared():
    f1 = cached_function(lambda x: x)
    f2 = cached_function(lambda y: y)
    assert type(f1) is type(f2)  # same spec -> same generated species class

    f3 = cached_function(lock=True)(lambda x: x)
    f4 = cached_function(cache_exceptions=(ValueError,))(lambda x: x)
    f5 = cached_function(lambda: 1)
    assert len({type(f) for f in [f1, f3, f4, f5]}) == 4  # distinct axes -> distinct species


def test_generated_source_is_registered():
    # All generated source (species __call__s and key makers) is registered with linecache so debuggers can step it.
    f = cached_function(lambda a, b=3: (a, b))

    call_file = type(f).__call__.__code__.co_filename
    assert call_file.startswith('<generated:')
    assert 'def _cached_call__' in ''.join(linecache.getlines(call_file))

    km_file = f._key_maker.__code__.co_filename  # type: ignore  # noqa
    assert km_file.startswith('<generated:')
    assert 'def __func__' in ''.join(linecache.getlines(km_file))


def test_direct_descriptor_call():
    # A decorated module-level-style function is descriptor-kinded but must remain directly callable as a plain cache.
    n = 0

    @cached_function
    def f(self):  # looks like a method - keyed as an ordinary first arg here
        nonlocal n
        n += 1
        return (self, n)

    assert f(1) == (1, 1)
    assert f(1) == (1, 1)
    assert f(2) == (2, 2)
    assert n == 2


##
# Axis-interaction matrix


class _MatrixError(Exception):
    pass


def _build_matrix_case(kind, shape, opts):
    state = {'n': 0}

    if kind == 'free':
        if shape == 'nullary':
            @cached_function(**opts)
            def f():
                state['n'] += 1
                return ('r',)
        else:
            @cached_function(**opts)
            def f(x):
                state['n'] += 1
                return ('r', x)
        return f, state, (lambda: f)

    if kind == 'boundmethod':
        class H:
            def nullary(self):
                state['n'] += 1
                return ('r',)

            def general(self, x):
                state['n'] += 1
                return ('r', x)

        f = cached_function(getattr(H(), shape), **opts)
        return f, state, (lambda: f)

    class C:
        if kind == 'method':
            if shape == 'nullary':
                @cached_function(**opts)
                def m(self):
                    state['n'] += 1
                    return ('r',)
            else:
                @cached_function(**opts)
                def m(self, x):
                    state['n'] += 1
                    return ('r', x)

        elif kind == 'classmethod':
            if shape == 'nullary':
                @cached_function(**opts)
                @classmethod
                def m(cls):
                    state['n'] += 1
                    return ('r',)
            else:
                @cached_function(**opts)
                @classmethod
                def m(cls, x):
                    state['n'] += 1
                    return ('r', x)

        elif kind == 'staticmethod':
            if shape == 'nullary':
                @cached_function(**opts)
                @staticmethod
                def m():
                    state['n'] += 1
                    return ('r',)
            else:
                @cached_function(**opts)
                @staticmethod
                def m(x):
                    state['n'] += 1
                    return ('r', x)

    o = C()
    holder = C if kind in ('classmethod', 'staticmethod') else o
    return (lambda *a, **kw: o.m(*a, **kw)), state, (lambda: holder.m)


@pytest.mark.parametrize('lock', [None, True])
@pytest.mark.parametrize('exc', [None, (_MatrixError,)])
@pytest.mark.parametrize('shape', ['nullary', 'general'])
@pytest.mark.parametrize('kind', ['free', 'boundmethod', 'method', 'classmethod', 'staticmethod'])
def test_matrix(kind, shape, lock, exc):
    opts = {}
    if lock is not None:
        opts['lock'] = lock
    if exc is not None:
        opts['cache_exceptions'] = exc

    call, state, get_wrapper = _build_matrix_case(kind, shape, opts)

    args = () if shape == 'nullary' else (7,)
    r = call(*args)
    for _ in range(2):
        assert call(*args) == r
    assert state['n'] == 1

    if shape == 'general':
        assert call(x=7) == r  # canonicalized to the same key
        assert state['n'] == 1
        assert call(8) == ('r', 8)
        assert state['n'] == 2

    n_before = state['n']
    get_wrapper().reset()
    assert call(*args) == r
    assert state['n'] == n_before + 1
