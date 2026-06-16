"""
Tests for the descriptor-protocol behavior of cached_function: per-instance binding & cache isolation, instance-dict
caching of bound wrappers, classmethod owner-caching, staticmethods, runtime-bound methods, and honoring of nested
custom __get__ descriptors.
"""
import functools

import pytest

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
    assert isinstance(b1, _DescriptorCachedFunction)
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
    assert c1.m._values is not c2.m._values  # type: ignore  # noqa


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
    assert isinstance(K.__dict__['cm'], _DescriptorCachedFunction)

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


def test_unbound_call_via_class_is_currently_broken():
    # KNOWN limitation (see function.py TODO "reconcile A().f() with A.f(A())"): calling an instance method through the
    # class with an explicit instance does not currently route through the instance cache and raises.
    class C:
        def __init__(self, v):
            self.v = v

        @cached_function
        def m(self):
            return ('m', self.v)

    c = C(1)
    assert c.m() == ('m', 1)
    with pytest.raises(TypeError):
        C.m(c)


def test_mismatched_attr_name_breaks_instance_caching():
    # KNOWN footgun: the bound-wrapper instance-dict key is derived from the *function* __name__, not the attribute name
    # it is bound under. When they differ, per-instance memoization is ineffective (recomputes each access).
    n = 0

    def _impl(self):
        nonlocal n
        n += 1
        return n

    class C:
        foo = cached_function(_impl)

    c = C()
    assert c.foo() == 1
    assert c.foo() == 2  # not cached: each `c.foo` access rebinds under key '_impl', never 'foo'
    assert '_impl' in c.__dict__
    assert 'foo' not in c.__dict__
