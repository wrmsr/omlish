import dataclasses as dc
import enum
import typing as ta

from ..base import MarshalContext
from ..base import Marshaler
from ..base import MarshalerFactory
from ..base import RecursiveMarshalerFactory
from ..base import RecursiveUnmarshalerFactory
from ..base import SetType
from ..base import UnmarshalContext
from ..base import UnmarshalerFactory
from ..base64 import BASE64_MARSHALER_FACTORY
from ..base64 import BASE64_UNMARSHALER_FACTORY
from ..dataclasses import DataclassMarshalerFactory
from ..dataclasses import DataclassUnmarshalerFactory
from ..datetimes import DatetimeMarshalerFactory
from ..enums import EnumMarshalerFactory
from ..enums import EnumUnmarshalerFactory
from ..exceptions import UnhandledSpecException
from ..factories import CompositeFactory
from ..factories import RecursiveSpecFactory
from ..factories import SpecCacheFactory
from ..factories import SpecMapFactory
from ..iterables import IterableMarshalerFactory
from ..iterables import IterableUnmarshalerFactory
from ..optionals import OptionalMarshalerFactory
from ..optionals import OptionalUnmarshalerFactory
from ..primitives import PRIMITIVE_MARSHALER_FACTORY
from ..primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..registries import Registry
from ..specs import Spec
from ..specs import spec_of
from ..uuids import UUID_MARSHALER_FACTORY
from ..uuids import UUID_UNMARSHALER_FACTORY
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

    mfs: list[MarshalerFactory] = [
        PRIMITIVE_MARSHALER_FACTORY,
        OptionalMarshalerFactory(),
        DataclassMarshalerFactory(),
        EnumMarshalerFactory(),
        UUID_MARSHALER_FACTORY,
        BASE64_MARSHALER_FACTORY,
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

    print()

    obj = Foo([420, 421], 'barf', Foo([1, 2], 'xxx', e=E.Y))
    print(obj)
    print()

    mc = MarshalContext(registry=reg, factory=mf)
    for _ in range(2):
        mobj = mc.make(type(obj)).marshal(mc, obj)
        print(mobj)
    print()

    ufs: list[UnmarshalerFactory] = [
        PRIMITIVE_UNMARSHALER_FACTORY,
        OptionalUnmarshalerFactory(),
        DataclassUnmarshalerFactory(),
        EnumUnmarshalerFactory(),
        UUID_UNMARSHALER_FACTORY,
        BASE64_UNMARSHALER_FACTORY,
        IterableUnmarshalerFactory(),
    ]

    uf: UnmarshalerFactory = SpecCacheFactory(  # noqa
        RecursiveUnmarshalerFactory(
            CompositeFactory(
                *ufs
            )
        )
    )

    uc = UnmarshalContext(registry=reg, factory=uf)
    for _ in range(2):
        uobj = uc.make(type(obj)).unmarshal(uc, mobj)
        print(uobj)
    print()
