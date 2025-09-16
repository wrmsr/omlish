# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..attrops import AttrOps
from ..attrops import attr_ops
from ..attrops import attr_repr


class TestAttrOps(unittest.TestCase):
    def test_attr_ops(self):
        class Point:
            def __init__(self, x: int, y: int) -> None:
                self.x, self.y = x, y

            __repr__, __hash__, __eq__ = AttrOps['Point'](lambda o: (o.x, o.y)).repr_hash_eq

        p1 = Point(20, 30)
        assert repr(p1) == 'Point(x=20, y=30)'

        p2 = Point(40, 50)
        assert repr(p2) == 'Point(x=40, y=50)'
        assert p1 != p2

        p1.x = 40
        assert repr(p1) == 'Point(x=40, y=30)'
        assert p1 != p2

        p2.y = 30
        assert repr(p2) == 'Point(x=40, y=30)'
        assert p1 == p2

    def test_install(self):
        class Point:
            def __init__(self, x: int, y: int) -> None:
                self.x, self.y = x, y

            AttrOps['Point'](lambda o: (o.x, o.y)).install(locals())

        p1 = Point(20, 30)
        assert repr(p1) == 'Point(x=20, y=30)'

        p2 = Point(40, 50)
        assert repr(p2) == 'Point(x=40, y=50)'
        assert p1 != p2

        p1.x = 40
        assert repr(p1) == 'Point(x=40, y=30)'
        assert p1 != p2

        p2.y = 30
        assert repr(p2) == 'Point(x=40, y=30)'
        assert p1 == p2

    def test_kwargs(self):
        class P0:
            def __init__(self, x: int, y: int) -> None:
                self.x, self.y = x, y

        class P1(P0):
            AttrOps['P1'](lambda o: (o.x, o.y)).install(locals())

        assert repr(P1(1, 2)) == 'P1(x=1, y=2)'

        class P2(P0):
            AttrOps['P2'](lambda o: (o.x, o.y), terse=True).install(locals())

        assert repr(P2(1, 2)) == 'P2(1, 2)'

        class P3(P0):
            AttrOps['P3'](lambda o: (o.x, (o.y, dict(repr_fn=lambda v: repr(v) if v > 3 else None)))).install(locals())

        assert repr(P3(1, 2)) == 'P3(x=1)'
        assert repr(P3(1, 4)) == 'P3(x=1, y=4)'

    def test_cache_hash(self):
        class A:
            hc = 0

            def __hash__(self):
                self.hc += 1
                return 42

        class B:
            def __init__(self, a: A) -> None:
                self.a = a

            AttrOps['B'](lambda o: (o.a,)).install(locals())

        b0 = B(A())
        assert b0.a.hc == 0
        assert isinstance(hash(b0), int)
        assert b0.a.hc == 1
        b1 = B(A())
        assert hash(b0) == hash(b1)
        assert b0.a.hc == 2
        assert b1.a.hc == 1

        class C(B):
            AttrOps['C'](lambda o: (o.a,), cache_hash=True).install(locals())

        c0 = C(A())
        assert c0.a.hc == 0
        assert isinstance(hash(c0), int)
        assert c0.a.hc == 1
        c1 = C(A())
        assert hash(c0) == hash(c1)
        assert c0.a.hc == 1
        assert c1.a.hc == 1


class TestAttrRepr(unittest.TestCase):
    def test_attr_repr(self):
        class Foo:
            def __init__(self, x, y, z):
                self.x = x
                self.y = y
                self.z = z

            __repr__ = attr_ops('x', 'y', 'z').repr

        self.assertEqual(repr(Foo(1, 2, 3)), 'Foo(x=1, y=2, z=3)')

        self.assertEqual(
            attr_repr(Foo(1, 2, 3), 'z', 'y', 'x', repr_filter=lambda v: v != 2),
            'Foo(z=3, x=1)',
        )

    def test_rec_repr(self):
        class RecFoo:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            __repr__ = attr_ops('x', 'y', recursive=True).repr

        f = RecFoo(1, RecFoo(2, None))
        f.y.y = f

        self.assertEqual(repr(f), 'RecFoo(x=1, y=RecFoo(x=2, y=...))')
