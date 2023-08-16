import abc
import dataclasses as _dc

import pytest

from ... import dataclasses as dc
from ... import lang


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
        D0()

    @dc.dataclass(frozen=True)
    class D1(Abc):
        def m(self):
            return 'm'

        p: str

    d1 = D1('p')
    assert d1.p == 'p'
    assert d1.p == 'p'
