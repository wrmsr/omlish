import typing as ta

from ...testing import assert_dicts_equal_ordered
from ..objects import Identity
from ..objects import SimpleProxy
from ..objects import mro_dict


def test_simple_proxy():
    class WrappedInt(SimpleProxy):
        __wrapped_attrs__ = ('__add__',)

    assert WrappedInt(4) + 2 == 6  # type: ignore

    class IncInt(SimpleProxy):
        def __add__(self, other):
            return self.__wrapped__.__add__(other + 1)

    assert IncInt(4) + 2 == 7


def test_mro_dict():
    class A:
        a = 0

    class B:
        b = 0

    class C(A, B):
        c = 0
        x = 'C'

    class D(A):
        d = 0
        x = 'D'

    class E(D, C):
        e = 0

    class F(C, D):
        f = 0

    def md(i, o=None, *, bu=False):
        return {k: v for k, v in mro_dict(i, o, bottom_up_key_order=bu).items() if not k.startswith('_')}

    assert_dicts_equal_ordered(md(E), {'e': 0, 'd': 0, 'x': 'D', 'c': 0, 'a': 0, 'b': 0})
    assert_dicts_equal_ordered(md(E, bu=True), {'b': 0, 'a': 0, 'c': 0, 'x': 'D', 'd': 0, 'e': 0})

    assert_dicts_equal_ordered(md(F), {'f': 0, 'c': 0, 'x': 'C', 'd': 0, 'a': 0, 'b': 0})
    assert_dicts_equal_ordered(md(F, bu=True), {'b': 0, 'a': 0, 'd': 0, 'x': 'C', 'c': 0, 'f': 0})

    assert_dicts_equal_ordered(md(E, o=D), {'d': 0, 'x': 'D', 'c': 0, 'a': 0, 'b': 0})
    assert_dicts_equal_ordered(md(E, o=C), {'c': 0, 'x': 'C', 'a': 0, 'b': 0})

    assert_dicts_equal_ordered(md(F, o=D), {'d': 0, 'x': 'D', 'a': 0, 'b': 0})
    assert_dicts_equal_ordered(md(F, o=C), {'c': 0, 'x': 'C', 'd': 0, 'a': 0, 'b': 0})

    assert_dicts_equal_ordered(md(E, o=D, bu=True), {'b': 0, 'a': 0, 'c': 0, 'x': 'D', 'd': 0})
    assert_dicts_equal_ordered(md(E, o=C, bu=True), {'b': 0, 'a': 0, 'c': 0, 'x': 'C'})

    assert_dicts_equal_ordered(md(F, o=D, bu=True), {'b': 0, 'a': 0, 'd': 0, 'x': 'D'})
    assert_dicts_equal_ordered(md(F, o=C, bu=True), {'b': 0, 'a': 0, 'd': 0, 'x': 'C', 'c': 0})


def test_test_mro_dict2():
    class A:
        x = 'A.x'
        y = 'A.y'
        z = 'A.z'

    class B(A):
        x = 'B.x'
        z = 'B.z'

    class C(A):
        y = 'C.y'
        z = 'C.z'

    class D(B, C):
        x = 'D.x'
        y = 'D.y'
        z = 'D.z'

    def md(i, o=None, *, bu=False):
        return {k: v for k, v in mro_dict(i, o, bottom_up_key_order=bu).items() if not k.startswith('_')}

    assert_dicts_equal_ordered(md(D, D), {'x': 'D.x', 'y': 'D.y', 'z': 'D.z'})
    assert_dicts_equal_ordered(md(D, C), {'y': 'C.y', 'z': 'C.z', 'x': 'A.x'})
    assert_dicts_equal_ordered(md(D, B), {'x': 'B.x', 'z': 'B.z', 'y': 'C.y'})
    assert_dicts_equal_ordered(md(D, A), {'x': 'A.x', 'y': 'A.y', 'z': 'A.z'})
    assert_dicts_equal_ordered(md(C, C), {'y': 'C.y', 'z': 'C.z', 'x': 'A.x'})
    assert_dicts_equal_ordered(md(C, A), {'x': 'A.x', 'y': 'A.y', 'z': 'A.z'})
    assert_dicts_equal_ordered(md(B, B), {'x': 'B.x', 'z': 'B.z', 'y': 'A.y'})
    assert_dicts_equal_ordered(md(B, A), {'x': 'A.x', 'y': 'A.y', 'z': 'A.z'})
    assert_dicts_equal_ordered(md(A, A), {'x': 'A.x', 'y': 'A.y', 'z': 'A.z'})


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
