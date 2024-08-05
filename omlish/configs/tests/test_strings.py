from ... import dataclasses as dc
from ..strings import interpolate_field
from ..strings import interpolate_strings


@dc.dataclass(frozen=True)
class Foo:
    i: int
    s: str = dc.field() | interpolate_field
    s2: str = 'nope'
    s3: str = dc.field(default='nope again') | interpolate_field


@dc.dataclass(frozen=True)
class ParentFoo:
    f: Foo


@dc.dataclass(frozen=True)
class ListFoo:
    l: list[Foo]


def test_strings():
    c = Foo(4, 'hi {there} bye')
    assert c.s == 'hi {there} bye'
    rpl = {'there': 'yes'}
    c2 = interpolate_strings(c, rpl)
    assert c2.s == 'hi yes bye'

    pc = ParentFoo(Foo(4, 'hi {there} bye'))
    assert pc.f.s == 'hi {there} bye'
    rpl = {'there': 'yes'}
    pc2 = interpolate_strings(pc, rpl)
    assert pc2.f.s == 'hi yes bye'

    lc = ListFoo([Foo(4, 'hi {there} bye'), Foo(5, 'bye {here} hi')])
    assert lc.l[0].s == 'hi {there} bye'
    assert lc.l[1].s == 'bye {here} hi'
    rpl = {'there': 'yes', 'here': 'no'}
    lc2 = interpolate_strings(lc, rpl)
    assert lc2.l[0].s == 'hi yes bye'
    assert lc2.l[1].s == 'bye no hi'
