import abc
import typing as ta

import pytest

from .. import pickling as pickling_  # noqa
from .. import enums as enums_


T = ta.TypeVar('T')


def test_enum():
    class E(enums_.Enum, sealed=True):
        x: int

    class E0(E):
        y: int

    class E1(E):
        z: int

    with pytest.raises(Exception):
        E(1)

    e0 = E0(0, 1)
    e1 = E1(1, 2)

    assert e0.x == 0
    assert e0.y == 1
    assert e1.x == 1
    assert e1.z == 2

    with pytest.raises(Exception):
        E2 = type('E2', (E,), {'__module__': 'barf'})  # noqa

    with pytest.raises(Exception):
        class E11(E1):
            pass

    class AE(enums_.Enum, sealed=True):
        x: int

        @abc.abstractmethod
        def f(self):
            raise NotImplementedError

    class AE0(AE):
        y: int

        def f(self):
            return '0'

    class AE1(AE):
        z: int

        def f(self):
            return '1'

    with pytest.raises(Exception):
        class AE2(AE):   # noqa
            z: int

    with pytest.raises(Exception):
        AE(1)

    ae0 = AE0(0, 1)
    ae1 = AE1(1, 2)

    assert ae0.x == 0
    assert ae0.y == 1
    assert ae0.f() == '0'
    assert ae1.x == 1
    assert ae1.z == 2
    assert ae1.f() == '1'


def test_abstract_enum():
    class A(enums_.Enum):
        a: int

    with pytest.raises(Exception):
        A(1)

    class B(A):
        b: int

    with pytest.raises(Exception):
        class B_(B):
            pass

    assert B(1, 2).a == 1
    assert B(1, 2).b == 2

    class C(A, abstract=True):
        c: int

    with pytest.raises(Exception):
        C(1, 2)

    class D(C):
        d: int

    assert D(1, 3, 4).a == 1
    assert D(1, 3, 4).c == 3
    assert D(1, 3, 4).d == 4

    with pytest.raises(Exception):
        class D_(D):
            pass

    class E(C):
        e: int

    assert E(1, 3, 5).a == 1
    assert E(1, 3, 5).c == 3
    assert E(1, 3, 5).e == 5

    with pytest.raises(Exception):
        class E_(E):
            pass

    class F(C, abstract=True):
        f: int

    with pytest.raises(Exception):
        F(1, 2, 7)

    class G(F):
        g: int

    assert G(1, 3, 5, 8).a == 1
    assert G(1, 3, 5, 8).c == 3
    assert G(1, 3, 5, 8).f == 5
    assert G(1, 3, 5, 8).g == 8

    with pytest.raises(Exception):
        class G_(G):
            pass


def test_enum_ident_eq():
    class A(enums_.Enum, eq=False):
        x: int

    class B(A):
        pass

    assert B(1) != B(1)


def test_value_enums():
    class BinOp(enums_.ValueEnum):
        glyph: str

    class BinOps(BinOp.Values):
        ADD = BinOp('+')
        SUB = BinOp('-')

    assert BinOps.SUB.name == 'SUB'
    assert BinOps.ADD.glyph == '+'

    assert BinOps.__members_by_name__ == {'ADD': BinOps.ADD, 'SUB': BinOps.SUB}
    assert BinOps.__members_by_value__ == {BinOps.ADD: 'ADD', BinOps.SUB: 'SUB'}

    # TODO:
    # assert BinOps('ADD') is BinOps.ADD
    # assert 'ADD' in BinOps
    # assert BinOps.ADD in BinOps
