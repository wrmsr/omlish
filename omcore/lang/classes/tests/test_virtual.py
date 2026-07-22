import abc
import enum
import types

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

    class D(P):
        pass

    with pytest.raises(TypeError):
        D()  # type: ignore

    virtual_check(P)(A)
    with pytest.raises(TypeError):
        virtual_check(P)(B)


def test_callable():
    with pytest.raises(TypeError):
        Callable()

    with pytest.raises(TypeError):
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


def test_virtual_static_and_class_methods():
    class HasStatics(Virtual):
        @staticmethod
        def sm():
            raise NotImplementedError

        @classmethod
        def cm(cls):
            raise NotImplementedError

    class Impl:
        @staticmethod
        def sm():
            pass

        @classmethod
        def cm(cls):
            pass

    assert issubclass(Impl, HasStatics)


def test_virtual_user_subclasshook():
    class Marked(Virtual):
        @classmethod
        def __subclasshook__(cls, subclass):
            return getattr(subclass, '__marked__', False)

    class Yes:
        __marked__ = True

    class No:
        pass

    assert issubclass(Yes, Marked)
    assert isinstance(Yes(), Marked)
    assert not issubclass(No, Marked)


def test_callable_checks():
    class WithCall:
        def __call__(self):
            pass

    class NoCall:
        pass

    class Color(enum.Enum):
        RED = 1

    # issubclass and isinstance must agree - issubclass looks its hook up on the metaclass.
    assert issubclass(types.FunctionType, Callable)
    assert issubclass(WithCall, Callable)
    assert not issubclass(NoCall, Callable)
    assert issubclass(type, Callable)

    assert isinstance(lambda: 0, Callable)
    assert isinstance(WithCall(), Callable)
    assert not isinstance(NoCall(), Callable)
    assert not isinstance(3, Callable)

    # A python-level metaclass __call__ makes the *class* callable, not its instances.
    assert not isinstance(Color.RED, Callable)
    assert not issubclass(Color, Callable)
