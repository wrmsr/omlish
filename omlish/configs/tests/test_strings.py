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


class StringInterpolator:
    def __init__(self, rpl: ta.Mapping[str, str]) -> None:
        super().__init__()
        self._rpl = rpl

    def __call__(self, v: T, *, _soft: bool = False) -> T:
        if dc.is_dataclass(v):
            kw = {}
            for f in dc.fields(v):  # type: ignore
                fv = getattr(v, f.name)
                nfv = self(fv, _soft=not f.metadata.get(InterpolateStringsMetadata))
                if fv is not nfv:
                    kw[f.name] = nfv
            if not kw:
                return v
            return dc.replace(v, **kw)

        elif isinstance(v, str):
            if not _soft:
                for rk, rv in self._rpl.items():
                    v = v.replace(rk, rv)
            return v

        else:
            return v


def interpolate_strings(v: T, rpl: ta.Mapping[str, str]) -> T:
    return StringInterpolator(rpl)(v)


##


@dc.dataclass(frozen=True)
class Foo:
    i: int
    s: str = dc.field() | interpolate_field


@dc.dataclass(frozen=True)
class ParentFoo:
    f: Foo


@dc.dataclass(frozen=True)
class ListFoo:
    l: list[Foo]


def test_strings():
    c = Foo(4, 'hi $THERE bye')
    assert c.s == 'hi $THERE bye'
    rpl = {'$THERE': 'yes'}
    c2 = interpolate_strings(c, rpl)
    assert c2.s == 'hi yes bye'

    pc = ParentFoo(Foo(4, 'hi $THERE bye'))
    assert pc.f.s == 'hi $THERE bye'
    rpl = {'$THERE': 'yes'}
    pc2 = interpolate_strings(pc, rpl)
    assert pc2.f.s == 'hi yes bye'

    lc = ListFoo([Foo(4, 'hi $THERE bye'), Foo(5, 'bye $HERE hi')])
    assert lc.l[0].s == 'hi $THERE bye'
    assert lc.l[1].s == 'bye $HERE hi'
    rpl = {'$THERE': 'yes', '$HERE': 'no'}
    lc2 = interpolate_strings(lc, rpl)
    assert lc2.l[0].s == 'hi yes bye'
    assert lc2.l[1].s == 'bye no hi'
