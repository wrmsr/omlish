# ruff: noqa: UP006 UP007
import typing as ta

from ... import dataclasses as dc
from ...lite import marshal as lmsh
from ..base import MarshalContext
from ..base import UnmarshalContext
from ..global_ import marshal
from ..global_ import unmarshal
from ..objects.helpers import update_fields_metadata
from ..objects.marshal import ObjectMarshaler
from ..objects.metadata import FieldInfo
from ..objects.metadata import ObjectSpecials
from ..objects.unmarshal import ObjectUnmarshaler
from ..registries import Registry
from ..trivial.nop import NOP_MARSHALER_UNMARSHALER


@dc.dataclass()
class C:
    i: int
    s: str
    x: dict[str, ta.Any]


def test_unknown_fields():
    fis = [
        FieldInfo(
            name='i',
            type=int,
            marshal_name='i',
            unmarshal_names=['i'],
        ),
        FieldInfo(
            name='s',
            type=str,
            marshal_name='s',
            unmarshal_names=['s'],
        ),
    ]

    ou = ObjectUnmarshaler(
        C,
        {fi.name: (fi, NOP_MARSHALER_UNMARSHALER) for fi in fis},
        specials=ObjectSpecials(unknown='x'),
    )
    c = ou.unmarshal(UnmarshalContext(Registry()), {'i': 420, 's': 'foo', 'qqq': 'huh'})
    assert c == C(i=420, s='foo', x={'qqq': 'huh'})

    om = ObjectMarshaler(
        [(fi, NOP_MARSHALER_UNMARSHALER) for fi in fis],
        specials=ObjectSpecials(unknown='x'),
    )
    o = om.marshal(MarshalContext(Registry()), c)
    assert o == {'i': 420, 's': 'foo', 'qqq': 'huh'}


def test_source_fields():
    fis = [
        FieldInfo(
            name='i',
            type=int,
            marshal_name='i',
            unmarshal_names=['i'],
        ),
        FieldInfo(
            name='s',
            type=str,
            marshal_name='s',
            unmarshal_names=['s'],
        ),
    ]

    ou = ObjectUnmarshaler(
        C,
        {fi.name: (fi, NOP_MARSHALER_UNMARSHALER) for fi in fis},
        specials=ObjectSpecials(source='x'),
        ignore_unknown=True,
    )
    c = ou.unmarshal(UnmarshalContext(Registry()), {'i': 420, 's': 'foo', 'qqq': 'huh'})
    assert c == C(i=420, s='foo', x={'i': 420, 's': 'foo', 'qqq': 'huh'})

    om = ObjectMarshaler(
        [(fi, NOP_MARSHALER_UNMARSHALER) for fi in fis],
        specials=ObjectSpecials(source='x'),
    )
    o = om.marshal(MarshalContext(Registry()), c)
    assert o == {'i': 420, 's': 'foo'}


##


@dc.dataclass()
class E0:
    i: int


@dc.dataclass()
class E1:
    s: str


@dc.dataclass()
class E2:
    f: float


@dc.dataclass()
@update_fields_metadata(['e1'], embed=True)
@update_fields_metadata(['e2'], embed=True, name='')
class E3:
    e0: E0
    e1: E1
    e2: E2
    b: bool


def test_embed():
    o = E3(
        E0(420),
        E1('ft'),
        E2(4.2),
        True,
    )
    m = marshal(o)
    print(m)
    u = unmarshal(m, E3)
    assert u == o


##


class Pt(ta.NamedTuple):
    i: int
    f: float
    s: str = 'foo'


def test_namedtuples():
    assert (d := marshal(p := Pt(1, 2.))) == {'i': 1, 'f': 2., 's': 'foo'}
    assert unmarshal(d, Pt) == p


##


def test_lite_name_overrides():
    @dc.dataclass
    class Junk:
        a: str
        b: str = dc.field(metadata={lmsh.OBJ_MARSHALER_FIELD_KEY: 'b!'})
        c: str = dc.field(default='default c', metadata={lmsh.OBJ_MARSHALER_FIELD_KEY: None})

    j = Junk('a', 'b', 'c')
    m = marshal(j)
    assert m == {'a': 'a', 'b!': 'b'}

    u: Junk = unmarshal(m, Junk)
    assert u == Junk('a', 'b', 'default c')


def test_lite_omit_if_none():
    @dc.dataclass
    class Junk:
        a: str
        b: ta.Optional[str]
        c: ta.Optional[str] = dc.field(metadata={lmsh.OBJ_MARSHALER_OMIT_IF_NONE: True})

    assert marshal(Junk('a', 'b', 'c')) == {'a': 'a', 'b': 'b', 'c': 'c'}
    assert marshal(Junk('a', None, None)) == {'a': 'a', 'b': None}
