"""
Tests for the descriptor-protocol behavior of cached_function: per-instance binding & cache isolation, instance-dict
caching of bound wrappers, classmethod owner-caching, staticmethods, runtime-bound methods, and honoring of nested
custom __get__ descriptors.
"""
import functools
import gc
import weakref

import pytest

from ..function import _BoundCachedFunction
from ..function import _DescriptorCachedFunction
from ..function import _FreeCachedFunction
from ..function import cached_function


##


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
    assert isinstance(b1, _BoundCachedFunction)
    assert isinstance(C.__dict__['m'], _DescriptorCachedFunction)


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
    assert c1.m() == ('m', 1)
    assert c1.m() == ('m', 1)
    assert n == 1
    assert c2.m() == ('m', 2)
    assert n == 2
    # distinct instances -> distinct value stores
    assert c1.m._v is not c2.m._v  # type: ignore  # noqa


def test_descriptor_and_bound_have_distinct_value_stores():
    class C:
        @cached_function
        def m(self):
            return 1

    c = C()
    desc = C.__dict__['m']
    bound = c.m
    assert desc._values is not bound._values  # type: ignore  # noqa


##


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

    assert K.cm() == 'K'
    assert K.cm() == 'K'
    assert calls == ['K']  # cached on owner K
    # owner-bound wrapper installed on the class itself
    assert isinstance(K.__dict__['cm'], _BoundCachedFunction)

    assert L.cm() == 'L'  # subclass recomputes against its own owner
    assert L.cm() == 'L'
    assert calls == ['K', 'L']


def test_classmethod_instance_access_shares_class_cache():
    calls = []

    class K:
        cv = 'K'

        @cached_function
        @classmethod
        def cm(cls):
            calls.append(cls.__name__)
            return cls.cv

    assert K.cm() == 'K'
    assert calls == ['K']
    assert K().cm() == 'K'  # instance access of a classmethod hits the class cache
    assert calls == ['K']


def test_classmethod_descriptor_direct_call():
    # The descriptor is itself a directly-callable species - for classmethods the direct call takes the unbound
    # (cls, ...) signature, keying every argument including cls.
    calls = []

    class K:
        @cached_function
        @classmethod
        def cm(cls, x):
            calls.append((cls, x))
            return (cls, x)

    class L(K):
        pass

    desc = K.__dict__['cm']  # must be grabbed before any attribute access installs a bound wrapper
    assert isinstance(desc, _DescriptorCachedFunction)

    assert desc(K, 1) == (K, 1)
    assert desc(K, 1) == (K, 1)
    assert calls == [(K, 1)]
    assert desc(L, 1) == (L, 1)  # cls is a key component
    assert calls == [(K, 1), (L, 1)]


##


def test_staticmethod():
    n = 0

    class C:
        @cached_function
        @staticmethod
        def s(x):
            nonlocal n
            n += 1
            return x * 2

    assert C.s(3) == 6
    assert C.s(3) == 6
    assert C().s(3) == 6
    assert n == 1
    assert C.s(4) == 8
    assert n == 2
    # staticmethod wrapping yields a shared (free) cached function, not a per-instance descriptor
    assert isinstance(C.__dict__['s'], _FreeCachedFunction)


##


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
    assert f(5) == 6
    assert f(5) == 6
    assert foo.c == 1
    assert f(6) == 7
    assert foo.c == 2


##


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
    assert c.m() == ('m', 7)
    assert cd.get_count == 1  # bound exactly once for this instance
    assert c.m() == ('m', 7)
    assert cd.get_count == 1  # memoized bound wrapper -> no further __get__


##


@pytest.mark.parametrize('bound_first', [True, False])
def test_do_you_seriously_globally_cache_self(bound_first):
    mc = 0

    class C:
        @cached_function
        def m(self):
            nonlocal mc
            mc += 1
            return self

    ws: weakref.WeakSet[C] = weakref.WeakSet()

    for _ in range(lc := 1000):
        c = C()
        ws.add(c)

        if bound_first:
            assert c.m() is c
            assert C.m(c) is c
        else:
            assert c.m() is c
            assert C.m(c) is c

        del c

    gc.collect()

    assert lc == mc

    assert not ws
