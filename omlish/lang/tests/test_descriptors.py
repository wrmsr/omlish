import pytest

from ..descriptors import AccessForbiddenError
from ..descriptors import access_forbidden
from ..descriptors import attr_property
from ..descriptors import classonly


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
