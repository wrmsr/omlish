import typing as ta

from ..objects import Identity
from ..objects import SimpleProxy


def test_simple_proxy():
    class WrappedInt(SimpleProxy):
        __wrapped_attrs__ = ('__add__',)

    assert WrappedInt(4) + 2 == 6  # type: ignore

    class IncInt(SimpleProxy):
        def __add__(self, other):
            return self.__wrapped__.__add__(other + 1)

    assert IncInt(4) + 2 == 7


##


def test_identity_object():
    class Pt(ta.NamedTuple):
        x: int
        y: int

    p1 = Pt(1, 2)
    p2 = Pt(1, 2)
    p3 = Pt(1, 3)

    assert p1 == p1  # noqa
    assert p1 == p2
    assert p1 != p3

    dct: dict = {}

    dct[p1] = 1
    dct[p3] = 3
    assert dct[p1] == 1
    assert dct[p2] == 1
    assert dct[p3] == 3

    dct[Identity(p1)] = 10
    assert dct[p1] == 1
    assert dct[Identity(p1)] == 10
    assert Identity(p2) not in dct

    dct[Identity(p2)] = 20
    assert dct[p1] == 1
    assert dct[Identity(p1)] == 10
    assert dct[Identity(p2)] == 20

    del dct[Identity(p1)]
    assert dct[p1] == 1
    assert Identity(p1) not in dct
    assert dct[Identity(p2)] == 20
