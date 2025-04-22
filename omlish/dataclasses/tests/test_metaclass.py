import abc
import typing as ta

import pytest

from ... import dataclasses as dc
from ... import lang


##


def test_confer_cache_hash():
    class A(dc.Frozen, lang.Abstract, cache_hash=True):
        pass

    assert dc.reflect(A).spec.cache_hash

    class B(A, lang.Final):
        pass

    assert dc.reflect(B).spec.cache_hash


def test_frozen_meta_hash():
    class Foo(dc.Frozen, eq=False):
        s: str

    class Foos(lang.Namespace):
        BAR = Foo('bar')
        BAZ = Foo('baz')

    assert Foos.BAR == Foos.BAR
    assert Foos.BAR != Foos.BAZ

    foo_to_str = {
        Foos.BAR: 'bar!',
        Foos.BAZ: 'baz!',
    }

    assert foo_to_str[Foos.BAR] == 'bar!'
    assert foo_to_str[Foos.BAZ] == 'baz!'
    assert Foo('abc') not in foo_to_str


def test_overrides():
    class A(dc.Frozen, abstract=True):
        @property
        @abc.abstractmethod
        def x(self) -> ta.Any:
            raise NotImplementedError

    assert lang.is_abstract_class(A)
    assert lang.get_abstract_methods(A) == frozenset(['x'])

    #

    try:
        class B(A):
            pass
    except lang.AbstractTypeError as te:
        assert str(te) == 'Cannot subclass abstract class B with abstract methods: x'  # noqa

    #

    class C(A, override=True):
        x: int

    assert not lang.is_abstract(C)
    assert C(5).x == 5

    #

    class D(A, abstract=True):
        pass

    assert lang.is_abstract_class(D)

    class E(D, override=True):
        x: str

    assert not lang.is_abstract(E)
    assert E('q').x == 'q'


##


def assert_non_abstract_class(cls, *args, **kwargs):
    assert isinstance(cls, type)
    assert not lang.is_abstract(cls)

    cls(*args, **kwargs)


def assert_abstract_class(cls):
    assert isinstance(cls, type)
    assert lang.is_abstract_class(cls)

    with pytest.raises(TypeError):
        cls()


def assert_non_final_class(cls):
    class Sub(cls):  # type: ignore
        pass


def assert_final_class(cls):
    with pytest.raises(lang.FinalTypeError):
        class Sub(cls):  # type: ignore
            pass


def test_final_subclasses():
    class A(dc.Frozen, final=True):
        pass

    assert_non_abstract_class(A)
    assert_final_class(A)

    #

    class B(dc.Frozen, abstract=True, final_subclasses=True):
        pass

    assert_abstract_class(B)
    assert_non_final_class(B)

    class C(B):
        pass

    assert_non_abstract_class(C)
    assert_final_class(C)

    #

    class D(B, abstract=True):
        pass

    assert_abstract_class(D)
    assert_non_final_class(D)

    class E(D):
        pass

    assert_non_abstract_class(E)
    assert_final_class(E)


def test_case():
    class A(dc.Case):
        pass

    assert_abstract_class(A)
    assert_non_final_class(A)

    class B(A):
        pass

    assert_non_abstract_class(B)
    assert_final_class(B)


def test_post_init():
    x = 0

    class Foo(dc.Data):
        def __post_init__(self):
            nonlocal x
            x += 1

    assert x == 0
    Foo()
    assert x == 1
    Foo()
    assert x == 2


def test_allow_redundant_decorator():
    with pytest.raises(TypeError):  # noqa
        @dc.dataclass(frozen=True)
        class Foo(dc.Box[int], allow_redundant_decorator=False):
            pass

    @dc.dataclass(frozen=True)
    class Bar(dc.Box[int]):
        pass

    with pytest.raises(TypeError):  # noqa
        @dc.dataclass()
        class Baz(dc.Box[int]):
            pass
