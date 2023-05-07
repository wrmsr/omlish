import abc
import typing as ta

import pytest

from ..classes import Abstract
from ..classes import Final
from ..classes import FinalException
from ..classes import Marker
from ..classes import Sealed
from ..classes import SealedException
from ..classes import is_abstract


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


def test_abstract():
    class C(Abstract):
        pass

    class D(C):
        pass

    class E(D, Abstract):
        pass

    class F(E):
        pass

    with pytest.raises(TypeError):
        C()
    D()
    with pytest.raises(TypeError):
        E()
    F()


def test_abstract2():
    class O(Abstract):
        pass

    assert is_abstract(O)

    with pytest.raises(TypeError):
        O()

    class A(Abstract):
        @abc.abstractmethod
        def f(self):
            pass

    assert is_abstract(A)

    with pytest.raises(TypeError):
        A()  # type: ignore

    class B(A, Abstract):
        pass

    with pytest.raises(TypeError):
        B()  # type: ignore

    class C(B):
        f = 0

    assert C()

    with pytest.raises(TypeError):
        class D(A):
            pass


def test_marker():
    class M(Marker):
        pass

    with pytest.raises(FinalException):
        class N(M):
            pass
    with pytest.raises(TypeError):
        M()

    assert repr(M) == '<M>'

    assert isinstance(M, M)
    assert issubclass(M, M)  # noqa

    class O(Marker):
        pass

    assert isinstance(O, O)
    assert issubclass(O, O)  # noqa

    assert not isinstance(M, O)
    assert not issubclass(M, O)
    assert not isinstance(O, M)
    assert not issubclass(O, M)


def test_is_abstract():
    class A(Abstract):
        pass

    assert is_abstract(A)

    class B(A):
        pass

    assert not is_abstract(B)

    class C(Abstract):

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            if cls.__name__ == 'D':
                assert is_abstract(cls)
            else:
                assert not is_abstract(cls)

    class D(C, Abstract):
        pass

    class E(D):
        pass
