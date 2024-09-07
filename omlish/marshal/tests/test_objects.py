import typing as ta

from ... import dataclasses as dc
from ..base import MarshalContext
from ..base import UnmarshalContext
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
