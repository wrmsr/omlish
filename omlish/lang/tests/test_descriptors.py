import pytest

from ..descriptors import access_forbidden
from ..descriptors import AccessForbiddenException
from ..descriptors import classonly


def test_access_forbidden():
    class C:
        f = access_forbidden()

    try:
        C.f  # noqa
    except AccessForbiddenException as e:
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
