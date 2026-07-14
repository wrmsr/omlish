import typing as ta
import unittest

from ..objects import mro_dict


K = ta.TypeVar('K')
V = ta.TypeVar('V')


def assert_dicts_equal_ordered(l: ta.Mapping[K, V], r: ta.Mapping[K, V]) -> None:
    assert list(l.items()) == list(r.items())


class TestMroDict(unittest.TestCase):
    def test_mro_dict(self):
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

    def test_test_mro_dict2(self):
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
