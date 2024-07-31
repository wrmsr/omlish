import inspect

import pytest

from ..descriptors import AccessForbiddenError
from ..descriptors import access_forbidden
from ..descriptors import attr_property
from ..descriptors import classonly
from ..descriptors import decorator


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

    @my_decorator
    def f(x):
        return x + 1

    for _ in range(2):
        assert f(3) == 5

    class Foo:
        def __init__(self, z):
            super().__init__()
            self.z = z

        z = 5

        @my_decorator
        def m(self, x):
            return self.z + x + 1

        @my_decorator
        @classmethod
        def c1(cls, x):
            return cls.z + x + 1

        @my_decorator
        @staticmethod
        def s1(x):
            return x + 1

        @classmethod
        @my_decorator
        def c2(cls, x):
            return cls.z + x + 1

        @staticmethod
        @my_decorator
        def s2(x):
            return x + 1

    f = Foo(4)
    for _ in range(2):
        assert f.m(2) == 8

    # FIXME? Could fix with __wrapped__ traversal to check if underlying is a Method, but slow and brittle...
    # assert Foo.m(Foo(4), 2) == 8

    assert Foo.c1(2) == 9
    assert Foo.s1(1) == 3

    assert Foo.c2(2) == 9
    assert Foo.s2(1) == 3

    for fn in [
        f.m,
        Foo.c1,
        Foo.s1,
        Foo.c2,
        Foo.s2,
    ]:
        assert list(inspect.signature(fn).parameters) == ['x']


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
