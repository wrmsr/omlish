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


def interpolate_fields(obj: T, replacements: ta.Mapping[str, str]) -> T:
    kw = {}
    for f in dc.fields(obj):
        if not f.metadata.get(InterpolateStringsMetadata):
            continue
        raise NotImplementedError
    if not kw:
        return obj
    return dc.replace(obj, **kw)


def test_strings():
    c = Foo(4, 'hi $THERE bye')
    assert c.s == 'hi $THERE bye'
    rpl = {'$THERE': 'yes'}
    c2 = interpolate_fields(c, rpl)
    assert c2.s == 'hi yes bye'
