import typing as ta

from ... import dataclasses as dc
from ..base import MarshalContext
from ..base import UnmarshalContext
from ..global_ import marshal
from ..global_ import unmarshal
from ..helpers import update_fields_metadata
from ..nop import NOP_MARSHALER_UNMARSHALER
from ..objects import FieldInfo
from ..objects import ObjectMarshaler
from ..objects import ObjectSpecials
from ..objects import ObjectUnmarshaler
from ..registries import Registry


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
