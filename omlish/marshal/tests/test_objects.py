import typing as ta

from ... import dataclasses as dc
from ..base import UnmarshalContext
from ..objects import FieldInfo
from ..objects import FieldMetadata
from ..objects import ObjectUnmarshaler
from ..primitives import PRIMITIVE_MARSHALER_UNMARSHALER
from ..registries import Registry


@dc.dataclass()
class C:
    i: int
    s: str
    x: dict[str, ta.Any]


def test_unknown_fields():
    ou = ObjectUnmarshaler(
        C,
        {
            'i': (
                FieldInfo(

                ),
                PRIMITIVE_MARSHALER_UNMARSHALER,
            ),
            's': (
                PRIMITIVE_MARSHALER_UNMARSHALER,
            ),
        },
        unknown_field='x',
    )

    c = ou.unmarshal(UnmarshalContext(Registry()), {'i': 420, 's': 'foo', 'qqq': 'huh'})
    print(c)
