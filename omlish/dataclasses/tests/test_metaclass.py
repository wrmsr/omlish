import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang


def test_confer_cache_hash():
    class A(dc.Frozen, lang.Abstract, cache_hash=True):
        pass

    assert dc.reflect(A).params_extras.cache_hash

    class B(A, lang.Final):
        pass

    assert dc.reflect(B).params_extras.cache_hash


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
        assert str(te) == 'Cannot subclass abstract class B with abstract methods: x'

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
