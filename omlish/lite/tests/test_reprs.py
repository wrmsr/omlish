# ruff: noqa: PT009
import unittest

from ..reprs import AttrRepr
from ..reprs import attr_repr


class TestAttrRepr(unittest.TestCase):
    def test_attr_repr(self):
        class Foo:
            def __init__(self, x, y, z):
                self.x = x
                self.y = y
                self.z = z

            __repr__ = AttrRepr.of('x', 'y', 'z')

        self.assertEqual(repr(Foo(1, 2, 3)), 'Foo(x=1, y=2, z=3)')

        self.assertEqual(
            attr_repr(Foo(1, 2, 3), 'z', 'y', 'x', value_filter=lambda v: v != 2),
            'Foo(z=3, x=1)',
        )
