import abc

import pytest

from ..virtual import Callable
from ..virtual import Virtual
from ..virtual import virtual_check


def test_virtual():
    class P(Virtual):
        @abc.abstractmethod
        def f(self):
            raise NotImplementedError

    with pytest.raises(TypeError):
        P()  # type: ignore

    class A:
        def f(self):
            pass

    class B:
        def g(self):
            pass

    A()

    assert issubclass(A, P)
    assert not issubclass(B, P)
    assert isinstance(A(), P)
    assert not isinstance(B(), P)

    class C(P):
        def f(self):
            pass

    with pytest.raises(TypeError):
        class D(P):
            pass

        D()  # type: ignore

    virtual_check(P)(A)
    with pytest.raises(TypeError):
        virtual_check(P)(B)


def test_callable():
    with pytest.raises(Exception):
        Callable()

    with pytest.raises(Exception):
        class C(Callable):  # noqa
            pass

    def f():
        pass

    assert isinstance(f, Callable)
    assert not isinstance(5, Callable)

    class D:
        pass

    class E:
        def __call__(self):
            pass

    assert isinstance(D, Callable)
    assert isinstance(E, Callable)
    assert isinstance(E(), Callable)
