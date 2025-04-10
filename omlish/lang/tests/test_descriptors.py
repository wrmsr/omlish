import functools
import inspect
import sys

import pytest

from ..descriptors import _DECORATOR_HANDLES_UNBOUND_METHODS
from ..descriptors import AccessForbiddenError
from ..descriptors import access_forbidden
from ..descriptors import attr_property
from ..descriptors import classonly
from ..descriptors import decorator
from ..descriptors import unwrap_func


def test_unwrap_func():
    assert unwrap_func(l := lambda: None) is l

    assert unwrap_func(functools.partial(l)) is l

    #

    def f(x):
        return x + 1

    @functools.wraps(f)
    def g(x):
        return f(x + 1)

    assert unwrap_func(f) is f
    assert unwrap_func(g) is f

    #

    def _m(self):
        pass

    def _c(cls):
        pass

    def _s():
        pass

    class C:
        m = _m
        c = classmethod(_c)
        s = staticmethod(_s)

    assert C().m is not _m
    assert unwrap_func(C().m) is _m

    assert C.c is not _c
    assert unwrap_func(C.c) is _c

    # assert C.s is not _s
    assert unwrap_func(C.s) is _s

    #

    p0 = lambda: None  # noqa
    p1 = functools.wraps(p0)(lambda: p0())
    p2 = functools.wraps(p1)(functools.partial(lambda: p1()))

    assert unwrap_func(p2) is p0


def test_access_forbidden():
    class C:
        f = access_forbidden()

    try:
        C.f  # noqa
    except AccessForbiddenError as e:
        assert e.name == 'f'  # noqa


def test_classonly():
    class Foo:
        @classonly
        @classmethod
        def foo(cls) -> str:
            return f'foo: {cls.__name__}'

    assert Foo.foo() == 'foo: Foo'
    with pytest.raises(TypeError):
        Foo().foo  # noqa


def test_attr_property():
    class C:
        def __init__(self, i: int, s: str) -> None:
            super().__init__()
            self._i = i
            self._s = s

        i: int = attr_property('_i')
        s: str = attr_property('_s')

    c = C(2, 'hi')
    assert c.i == 2
    assert c.s == 'hi'


def test_single_decorator():
    @decorator
    def my_decorator(fn, x):
        return fn(x + 1)

    def _f(x):
        return x + 1
    f = my_decorator(_f)

    for _ in range(2):
        assert f(3) == 5

    assert list(inspect.signature(f).parameters) == ['x']
    assert unwrap_func(f) is _f

    def _m(self, x):
        return self.z + x + 1

    def _c1(cls, x):
        return cls.z + x + 1

    def _s1(x):
        return x + 1

    def _c2(cls, x):
        return cls.z + x + 1

    def _s2(x):
        return x + 1

    class Foo:
        def __init__(self, z):
            super().__init__()
            self.z = z

        z = 5

        m = my_decorator(_m)

        c1 = my_decorator(classmethod(_c1))
        s1 = my_decorator(staticmethod(_s1))

        c2 = classmethod(my_decorator(_c2))  # type: ignore
        s2 = staticmethod(my_decorator(_s2))

    f = Foo(4)
    for _ in range(2):
        assert f.m(2) == 8

    if _DECORATOR_HANDLES_UNBOUND_METHODS:
        assert Foo.m(Foo(4), 2) == 8

    assert Foo.c1(2) == 9
    assert Foo.s1(1) == 3

    # FIXME: https://github.com/python/cpython/commit/7f9a99e8549b792662f2cd28bf38a4d4625bd402 :|
    # See: https://github.com/python/cpython/issues/63272
    if sys.version_info < (3, 13):
        assert Foo.c2(2) == 9
        assert Foo.s2(1) == 3

    assert list(inspect.signature(f.m).parameters) == ['x']
    assert unwrap_func(f.m) is _m

    for fn, wfn in [
        (Foo.c1, _c1),
        (Foo.s1, _s1),
        (Foo.c2, _c2),
        (Foo.s2, _s2),
    ]:
        assert list(inspect.signature(fn).parameters) == ['x']
        assert unwrap_func(fn) is wfn

    assert list(inspect.signature(Foo.m).parameters) == ['self', 'x']
    assert unwrap_func(Foo.m) is _m


def test_double_decorator():
    def my_decorator(y):
        @decorator
        def inner(fn, x):
            return fn(x + y)
        return inner

    @my_decorator(2)
    def f(x):
        return x + 1

    for _ in range(2):
        assert f(3) == 6


def test_nested_decorator():
    @decorator
    def my_decorator1(fn, x):
        return fn(x + 1)

    @decorator
    def my_decorator2(fn, x):
        return fn(x * 2)

    def _m(self, x):
        return self.z + x + 1

    def _c(cls, x):
        return cls.z + x + 1

    class Foo:
        z = 9

        def __init__(self, z):
            self.z = z

        m1 = my_decorator1(my_decorator2(_m))
        m2 = my_decorator2(my_decorator1(_m))

        c1 = my_decorator1(my_decorator2(classmethod(_c)))
        c2 = my_decorator1(classmethod(my_decorator2(_c)))
        c3 = my_decorator1(my_decorator2(classmethod(my_decorator2(my_decorator1(_c)))))

    assert Foo(3).m1(2) == 10
    assert Foo(3).m2(2) == 9

    assert unwrap_func(Foo(3).m1) is _m
    assert unwrap_func(Foo(3).m2) is _m

    if _DECORATOR_HANDLES_UNBOUND_METHODS:
        print(Foo.m1(Foo(3), 2))
        print(Foo.m2(Foo(3), 2))

    assert unwrap_func(Foo.m1) is _m
    assert unwrap_func(Foo.m2) is _m

    assert Foo.c1(9) == 30

    # FIXME: https://github.com/python/cpython/commit/7f9a99e8549b792662f2cd28bf38a4d4625bd402 :|
    if sys.version_info < (3, 13):
        assert Foo.c2(9) == 30
        assert Foo.c3(9) == 51

    assert unwrap_func(Foo.c1) is _c
    assert unwrap_func(Foo.c2) is _c
    assert unwrap_func(Foo.c3) is _c
