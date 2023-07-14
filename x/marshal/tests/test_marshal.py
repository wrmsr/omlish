import dataclasses as dc
import enum
import typing as ta

from ..base import MarshalContext
from ..base import Marshaler
from ..base import MarshalerFactory
from ..base import RecursiveMarshalerFactory
from ..base import SetType
from ..base64 import Base64MarshalerFactory
from ..dataclasses import DataclassMarshalerFactory
from ..datetimes import DatetimeMarshalerFactory
from ..enums import EnumMarshalerFactory
from ..exc import UnhandledSpecException
from ..factories import CompositeFactory
from ..factories import RecursiveSpecFactory
from ..factories import SpecCacheFactory
from ..factories import SpecMapFactory
from ..iterables import IterableMarshalerFactory
from ..optionals import OptionalMarshalerFactory
from ..primitives import PRIMITIVE_MARSHALER
from ..primitives import PRIMITIVE_MARSHALER_FACTORY
from ..registries import Registry
from ..specs import Spec
from ..specs import spec_of
from ..uuids import UuidMarshalerFactory
from .foox import Foox


class E(enum.Enum):
    X = enum.auto()
    Y = enum.auto()
    Z = enum.auto()


@dc.dataclass(frozen=True)
class Foo(Foox):
    s: str
    f: ta.Optional['Foo'] = None
    e: ta.Optional[E] = None


def test_marshal():
    # reg = Registry()
    # reg.register(spec_of(int), SetType(marshaler=PrimitiveMarshaler()))

    mfs: ta.List[MarshalerFactory] = [  # noqa
        PRIMITIVE_MARSHALER_FACTORY,
        OptionalMarshalerFactory(),
        DataclassMarshalerFactory(),
        EnumMarshalerFactory(),
        UuidMarshalerFactory(),
        Base64MarshalerFactory(),
        DatetimeMarshalerFactory(),
        IterableMarshalerFactory(),
    ]

    mf: MarshalerFactory = SpecCacheFactory(  # noqa
        RecursiveMarshalerFactory(
            CompositeFactory(
                *mfs
            )
        )
    )

    reg = Registry()
    mc = MarshalContext(registry=reg, factory=mf)
    for _ in range(2):
        print(mc.make(Foo).marshal(mc, Foo([420, 421], 'barf', Foo([1, 2], 'xxx', e=E.Y))))
