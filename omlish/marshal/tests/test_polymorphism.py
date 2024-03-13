import dataclasses as dc
import enum
import typing as ta

from .. import polymorphism as poly
from ..base import MarshalContext
from ..base import UnmarshalContext
from ..global_ import marshal
from ..global_ import unmarshal
from ..registries import Registry
from ..standard import new_standard_marshaler_factory
from ..standard import new_standard_unmarshaler_factory
from .foox import Foox
from ..factories import TypeCacheFactory
from ..any import ANY_MARSHALER_FACTORY
from ..any import ANY_UNMARSHALER_FACTORY
from ..base import MarshalerFactory
from ..base import RecursiveMarshalerFactory
from ..base import RecursiveUnmarshalerFactory
from ..base import UnmarshalerFactory
from ..base64 import BASE64_MARSHALER_FACTORY
from ..base64 import BASE64_UNMARSHALER_FACTORY
from ..dataclasses import DataclassMarshalerFactory
from ..dataclasses import DataclassUnmarshalerFactory
from ..datetimes import DATETIME_MARSHALER_FACTORY
from ..datetimes import DATETIME_UNMARSHALER_FACTORY
from ..enums import EnumMarshalerFactory
from ..enums import EnumUnmarshalerFactory
from ..factories import CompositeFactory
from ..factories import TypeCacheFactory
from ..iterables import IterableMarshalerFactory
from ..iterables import IterableUnmarshalerFactory
from ..mappings import MappingMarshalerFactory
from ..mappings import MappingUnmarshalerFactory
from ..optionals import OptionalMarshalerFactory
from ..optionals import OptionalUnmarshalerFactory
from ..primitives import PRIMITIVE_MARSHALER_FACTORY
from ..primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..uuids import UUID_MARSHALER_FACTORY
from ..uuids import UUID_UNMARSHALER_FACTORY
from ..polymorphism import PolymorphismUnmarshalerFactory
from ..polymorphism import PolymorphismUnmarshaler
from ..polymorphism import PolymorphismMarshalerFactory
from ..polymorphism import PolymorphismMarshaler


@dc.dataclass(frozen=True)
class PB:
    a: str


@dc.dataclass(frozen=True)
class PS0(PB):
    b: str


@dc.dataclass(frozen=True)
class PS1(PB):
    b: int


@dc.dataclass(frozen=True)
class PS2(PB):
    b: PB


def test_polymorphism():
    p = poly.Polymorphism(
        PB,
        [
            poly.Impl(PS0, 's0'),
            poly.Impl(PS1, 's1'),
        ],
    )

    mf: MarshalFactory = TypeCacheFactory(  # noqa
        RecursiveMarshalerFactory(
            CompositeFactory(
                PolymorphismMarshalerFactory(p),
                DataclassMarshalerFactory(),
                PRIMITIVE_MARSHALER_FACTORY,
            )
        )
    )

    umf: UnmarshalFactory = TypeCacheFactory(  # noqa
        RecursiveUnmarshalerFactory(
            CompositeFactory(
                PolymorphismUnmarshalerFactory(p),
                DataclassUnmarshalerFactory(),
                PRIMITIVE_UNMARSHALER_FACTORY,
            )
        )
    )

    p = PS2('0', PS1('1', 420))

    reg = Registry()

    mc = MarshalContext(registry=reg, factory=mf)
    v = mc.make(PB).marshal(mc, p)
    print(v)
