import typing as ta

import pytest

from ..restrict import Final
from ..restrict import FinalException
from ..restrict import NoBool
from ..restrict import Sealed
from ..restrict import SealedException
from ..restrict import no_bool


def test_final():
    class A:
        pass

    A()

    class B(A, Final):
        pass

    B()

    with pytest.raises(FinalException):
        class C(B):
            pass

    T = ta.TypeVar('T')

    class D(ta.Generic[T], Final):
        pass

    D()
    D[int]  # noqa

    with pytest.raises(FinalException):
        class E(D[int]):
            pass


def test_sealed():
    class A(Sealed):
        __module__ = 'a'

    class B(A):
        __module__ = 'a'

    with pytest.raises(SealedException):
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
