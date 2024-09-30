import typing as ta

from ... import dataclasses as dc
from ..base import MarshalContext
from ..base import UnmarshalContext
from ..global_ import marshal
from ..global_ import unmarshal
from ..helpers import update_fields_metadata
from ..objects import FieldInfo
from ..objects import ObjectMarshaler
from ..objects import ObjectUnmarshaler
from ..primitives import PRIMITIVE_MARSHALER_UNMARSHALER
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
        {fi.name: (fi, PRIMITIVE_MARSHALER_UNMARSHALER) for fi in fis},
        unknown_field='x',
    )
    c = ou.unmarshal(UnmarshalContext(Registry()), {'i': 420, 's': 'foo', 'qqq': 'huh'})
    print(c)

    om = ObjectMarshaler(
        [(fi, PRIMITIVE_MARSHALER_UNMARSHALER) for fi in fis],
        unknown_field='x',
    )
    o = om.marshal(MarshalContext(Registry()), c)
    print(o)


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
