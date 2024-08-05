from ... import dataclasses as dc
from ... import lang


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


class Foo:
    i: int
    s: str = dc.field() | interpolate_field


def test_strings():
    pass
