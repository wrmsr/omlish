# ruff: noqa: PT009
import dataclasses as dc
import unittest

from ..rewriting import RawConfigMetadata
from ..strings import format_config_strings


@dc.dataclass(frozen=True)
class Foo:
    i: int
    s: str = dc.field(metadata={RawConfigMetadata: True})
    s2: str = 'no{pe'
    s3: str = dc.field(default='no{pe again', metadata={RawConfigMetadata: False})


@dc.dataclass(frozen=True)
class ParentFoo:
    f: Foo


@dc.dataclass(frozen=True)
class ListFoo:
    l: list[Foo]


class TestStrings(unittest.TestCase):
    def test_strings(self):
        c = Foo(4, 'hi {there} bye')
        assert c.s == 'hi {there} bye'
        rpl = {'there': 'yes'}
        c2 = format_config_strings(c, rpl)
        self.assertEqual(c2.s, 'hi yes bye')
        self.assertEqual(c2.s2, 'no{pe')
        self.assertEqual(c2.s3, 'no{pe again')

        pc = ParentFoo(Foo(4, 'hi {there} bye'))
        self.assertEqual(pc.f.s, 'hi {there} bye')
        rpl = {'there': 'yes'}
        pc2 = format_config_strings(pc, rpl)
        self.assertEqual(pc2.f.s, 'hi yes bye')

        lc = ListFoo([Foo(4, 'hi {there} bye'), Foo(5, 'bye {here} hi')])
        self.assertEqual(lc.l[0].s, 'hi {there} bye')
        self.assertEqual(lc.l[1].s, 'bye {here} hi')
        rpl = {'there': 'yes', 'here': 'no'}
        lc2 = format_config_strings(lc, rpl)
        self.assertEqual(lc2.l[0].s, 'hi yes bye')
        self.assertEqual(lc2.l[1].s, 'bye no hi')
