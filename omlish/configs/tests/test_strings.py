import types
import typing as ta

from ... import dataclasses as dc
from ... import lang


T = ta.TypeVar('T')


class InterpolateStringsMetadata(lang.Marker):
    pass


@dc.field_modifier
def secret_or_key_field(f: dc.Field) -> dc.Field:
    return dc.update_field_metadata(f, {
        InterpolateStringsMetadata: True,
    })


@dc.field_modifier
def interpolate_field(f: dc.Field) -> dc.Field:
    return dc.update_field_metadata(f, {InterpolateStringsMetadata: True})


@dc.dataclass(frozen=True)
class Foo:
    i: int
    s: str = dc.field() | interpolate_field


@dc.dataclass(frozen=True)
class Foo2:
    l: list[Foo]


def interpolate_fields(obj: T, replacements: ta.Mapping[str, str]) -> T:
    kw = {}

    for f in dc.fields(obj):  # type: ignore
        if not f.metadata.get(InterpolateStringsMetadata):
            continue
        v = getattr(obj, f.name)
        if not isinstance(v, str):
            raise TypeError(v)
        nv = v
        for rk, rv in replacements.items():
            nv = nv.replace(rk, rv)
        if nv != v:
            kw[f.name] = nv

    if not kw:
        return obj
    return dc.replace(obj, **kw)


def test_strings():
    c = Foo(4, 'hi $THERE bye')
    assert c.s == 'hi $THERE bye'
    rpl = {'$THERE': 'yes'}
    c2 = interpolate_fields(c, rpl)
    assert c2.s == 'hi yes bye'

    lc = Foo2([Foo(4, 'hi $THERE bye'), Foo(5, 'bye $HERE hi')])
    assert lc.l[0].s == 'hi $THERE bye'
    assert lc.l[1].s == 'bye $HERE hi'
    rpl = {'$THERE': 'yes', '$HERE': 'no'}
    lc2 = interpolate_fields(c, rpl)
    assert lc2.l[0].s == 'hi yes bye'
    assert lc2.l[1].s == 'bye no hi'
