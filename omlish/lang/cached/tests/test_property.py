import pytest

from ..property import _IGNORE
from ..property import _CachedProperty
from ..property import cached_property


##


def test_property():
    n = 0

    class C:
        @cached_property
        def x(self) -> int:
            nonlocal n
            n += 1
            return n

    c = C()
    assert c.x == 1
    assert c.x == 1
    assert C().x == 2
    assert C().x == 3


def test_class_access_returns_descriptor():
    class C:
        @cached_property
        def x(self):
            return 1

    assert isinstance(C.x, _CachedProperty)


##


def test_set_same_value_is_noop():
    class C:
        @cached_property
        def x(self):
            return 42

    c = C()
    assert c.x == 42
    c.x = 42  # equal to cached -> allowed no-op
    assert c.x == 42


def test_set_different_value_raises():
    class C:
        @cached_property
        def x(self):
            return 42

    c = C()
    assert c.x == 42
    with pytest.raises(TypeError):
        c.x = 99


def test_set_before_get_raises():
    class C:
        @cached_property
        def x(self):
            return 42

    c = C()
    with pytest.raises(TypeError):
        c.x = 7  # cannot prime by setting before first get
    assert c.x == 42


def test_delete_raises():
    class C:
        @cached_property
        def x(self):
            return 42

    c = C()
    assert c.x == 42
    with pytest.raises(TypeError):
        del c.x


##


def test_ignore_if():
    n = 0

    class C:
        @cached_property(ignore_if=lambda v: v is None)
        def y(self):
            nonlocal n
            n += 1
            return n

    c = C()
    c.y = None  # ignored by ignore_if -> not stored
    assert c.y == 1  # so the getter still runs
    assert n == 1
    assert c.y == 1  # now cached
    assert n == 1


def test_ignore_sentinel_return_not_cached():
    n = 0

    class C:
        @cached_property
        def x(self):
            nonlocal n
            n += 1
            return _IGNORE if n < 3 else 'real'

    c = C()
    # Each access goes into a fresh local so type narrowing from one assertion does not leak into the next.
    a = c.x
    assert a is None  # n=1: _IGNORE -> None, not cached
    b = c.x
    assert b is None  # n=2: still not cached
    d = c.x
    assert d == 'real'  # n=3: now cached
    e = c.x
    assert e == 'real'
    assert n == 3


##


def test_missing_name_raises():
    class C:
        pass

    C.z = cached_property(lambda self: 5)  # type: ignore  # assigned after class body -> __set_name__ never called
    with pytest.raises(TypeError):
        C().z  # type: ignore  # noqa


def test_explicit_name():
    class C:
        pass

    # explicit name lets it work even without __set_name__
    C.z = cached_property(lambda self: 5, name='z')  # type: ignore
    assert C().z == 5  # type: ignore


def test_wraps_a_property():
    class C:
        x = cached_property(property(lambda self: 42))

    c = C()
    assert c.x == 42
    assert c.x == 42


##


def test_inheritance_independent_caching():
    n = 0

    class B:
        @cached_property
        def x(self):
            nonlocal n
            n += 1
            return n

    class D(B):
        pass

    b = B()
    d = D()
    assert b.x == 1
    assert d.x == 2  # separate instance -> separate cache slot
    assert b.x == 1
    assert d.x == 2
    assert n == 2


##


def test_transient_stores_in_transient_dict():
    class C:
        @cached_property(transient=True)
        def w(self):
            return 'w'

    c = C()
    assert c.w == 'w'
    assert 'w' not in c.__dict__  # not in the normal instance dict
    assert '__transient_dict__' in c.__dict__


def test_transient_caches_within_session():
    n = 0

    class C:
        @cached_property(transient=True)
        def w(self):
            nonlocal n
            n += 1
            return n

    c = C()
    assert c.w == 1
    assert c.w == 1
    assert n == 1
