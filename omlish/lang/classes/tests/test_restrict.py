import abc
import typing as ta

import pytest

from ..abstract import Abstract
from ..abstract import AbstractTypeError
from ..restrict import AnySensitive
from ..restrict import Final
from ..restrict import FinalTypeError
from ..restrict import NoBool
from ..restrict import Sealed
from ..restrict import SealedError
from ..restrict import Sensitive
from ..restrict import no_bool


def test_final():
    class A:
        pass

    A()

    class B(A, Final):
        pass

    B()

    with pytest.raises(FinalTypeError):
        class C(B):
            pass

    T = ta.TypeVar('T')

    class D(ta.Generic[T], Final):
        pass

    D()
    D[int]  # noqa

    with pytest.raises(FinalTypeError):
        class E(D[int]):
            pass


def test_abstract_final_mro():
    class A:
        def foo(self):
            pass

    class B(Abstract):
        @abc.abstractmethod
        def foo(self):
            pass

    class C(A, B, Final):  # noqa
        pass

    with pytest.raises(AbstractTypeError):
        class D(B, Final):  # noqa
            pass


def test_sealed():
    class A(Sealed):
        __module__ = 'a'

    class B(A):
        __module__ = 'a'

    with pytest.raises(SealedError):
        class C(A):
            __module__ = 'c'

    class D(B):
        __module__ = 'd'


def test_no_bool():
    @no_bool
    def f():
        return 1

    assert f() == 1
    assert bool(f())
    with pytest.raises(TypeError):
        bool(f)

    class C(NoBool):
        pass

    assert C  # type: ignore
    with pytest.raises(TypeError):
        bool(C())


def test_sensitive():
    with pytest.raises(TypeError):
        AnySensitive()

    assert not issubclass(str, Sensitive)
    assert not issubclass(str, AnySensitive)
    assert not isinstance('foo', Sensitive)
    assert not isinstance('foo', AnySensitive)

    class Foo(Sensitive):
        pass

    assert issubclass(Foo, Sensitive)
    assert issubclass(Foo, AnySensitive)
    assert isinstance(Foo(), Sensitive)
    assert isinstance(Foo(), AnySensitive)

    class Bar:
        __sensitive__ = True

    assert not issubclass(Bar, Sensitive)
    assert issubclass(Bar, AnySensitive)
    assert not isinstance(Bar(), Sensitive)
    assert isinstance(Bar(), AnySensitive)

    class Baz:
        __sensitive__ = False

    assert not issubclass(Baz, Sensitive)
    assert issubclass(Baz, AnySensitive)
    assert not isinstance(Baz(), Sensitive)
    assert isinstance(Baz(), AnySensitive)


def test_lite_secret_sensitive():
    from ....lite.secrets import Secret

    assert not issubclass(Secret, Sensitive)
    assert issubclass(Secret, AnySensitive)
    assert not isinstance(Secret(value='foo'), Sensitive)
    assert isinstance(Secret(value='foo'), AnySensitive)


def test_sensitive_register():
    class Foo:
        pass

    assert not issubclass(Foo, Sensitive)
    assert not issubclass(Foo, AnySensitive)
    assert not isinstance(Foo(), Sensitive)
    assert not isinstance(Foo(), AnySensitive)

    AnySensitive.register(Foo)

    assert not issubclass(Foo, Sensitive)
    assert issubclass(Foo, AnySensitive)
    assert not isinstance(Foo(), Sensitive)
    assert isinstance(Foo(), AnySensitive)
