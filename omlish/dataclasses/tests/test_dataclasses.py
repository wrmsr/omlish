import abc
import dataclasses as _dc
import typing as ta

import pytest

from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl  # noqa


T = ta.TypeVar('T')


def test_simple():
    @dc.dataclass()
    class Foo:
        x: int
        y: int

    @_dc.dataclass()
    class Bar:
        x: int
        z: int

    @dc.dataclass()
    class Baz0(Foo, Bar):
        a: int

    @_dc.dataclass()
    class Baz1(Foo, Bar):
        a: int

    print(Foo(1, 2))


def test_check_coerce():
    @dc.dataclass()
    class Bar:
        x: int = dc.xfield(coerce=int, check=lambda x: x < 10)

    print(Bar(4))
    print(Bar('4'))  # type: ignore

    with pytest.raises(dc.CheckException):
        Bar(11)


def test_check_init():
    @dc.dataclass()
    class C:
        x: int = dc.xfield(check=lambda x: x > 10)

        dc.check(lambda x: x < 20)

        @dc.check  # noqa
        @staticmethod
        def _check_x_not_15(x: int) -> bool:
            return x != 15

        @dc.init
        def _init_foo(self) -> None:
            self._foo = 100

    c = C(11)
    assert c._foo == 100

    with pytest.raises(Exception):
        C(9)


def test_mcls():
    class C(dc.Data):
        x: int

    assert C(10).x == 10


def test_reflect():
    @dc.dataclass()
    class Foo:
        x: int
        y: int

    @_dc.dataclass()
    class Bar:
        x: int
        z: int

    @dc.dataclass()
    class Baz0(Foo, Bar):
        a: int

    ref = dc.reflect(Baz0)
    print(ref)
    print(ref.params)
    print(ref.params12)
    print(ref.params_extras)
    print(ref.merged_metadata)


def test_abc():
    class Abc(abc.ABC):
        def foo(self):
            return 'foo'

        @abc.abstractmethod
        def m(self):
            raise NotImplementedError

        @property
        @abc.abstractmethod
        def p(self):
            raise NotImplementedError

    class D0(Abc):
        pass
    with pytest.raises(TypeError):
        D0()  # type: ignore

    @dc.dataclass(frozen=True)
    class D1(Abc):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d1 = D1('p')
    assert d1.p == 'p'
    assert d1.p == 'p'
    with pytest.raises(dc.FrozenInstanceError):
        d1.p = 'p2'  # type: ignore  # noqa
    assert d1.foo() == 'foo'

    @dc.dataclass()
    class D2(Abc):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d2 = D2('p')
    assert d2.p == 'p'
    assert d2.p == 'p'
    d2.p = 'p2'
    assert d2.p == 'p2'

    ##

    class Abstract(lang.Abstract):
        def foo(self):
            return 'foo'

        @abc.abstractmethod
        def m(self):
            raise NotImplementedError

        @property
        @abc.abstractmethod
        def p(self):
            raise NotImplementedError

    with pytest.raises(TypeError):
        class D3(Abstract):
            pass

    @dc.dataclass(frozen=True)
    class D4(Abstract):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d4 = D4('p')
    assert d4.p == 'p'
    assert d4.p == 'p'
    with pytest.raises(dc.FrozenInstanceError):
        d4.p = 'p2'  # type: ignore  # noqa
    assert d4.foo() == 'foo'

    @dc.dataclass()
    class D5(Abstract):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d5 = D5('p')
    assert d5.p == 'p'
    assert d5.p == 'p'
    d5.p = 'p5'
    assert d5.p == 'p5'


def test_reorder():
    @dc.dataclass()
    class A:
        x: int
        y: int = 3

    @dc.dataclass(reorder=True)  # type: ignore
    class B(A):  # noqa
        z: int  # type: ignore

    b = B(1, 2)  # type: ignore
    assert b.x == 1
    assert b.z == 2
    assert b.y == 3


def test_generics():
    @dc.dataclass()
    class Box(ta.Generic[T]):
        v: T

    rty0 = rfl.type_(Box[int])  # noqa

    assert Box[int](5).v == 5

    @dc.dataclass()
    class IntBox(Box[int]):
        pass

    rty1 = rfl.type_(IntBox)  # noqa

    assert IntBox(5).v == 5

    info = dc.reflect(IntBox)
    print(info.field_owners)
    print(info.mro_type_args)


def test_confer_frozen():
    class A(dc.Frozen):
        x: int
