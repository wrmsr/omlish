import dataclasses as dc
import typing as ta

from ..base import MarshalContext
from ..base import Marshaler
from ..base import MarshalerFactory
from ..base import RecursiveMarshalerFactory
from ..base import SetType
from ..dataclasses import DataclassMarshalerFactory
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


@dc.dataclass(frozen=True)
class Foo:
    il: list[int]
    s: str
    f: ta.Optional['Foo'] = None


def test_marshal():
    # reg = Registry()
    # reg.register(spec_of(int), SetType(marshaler=PrimitiveMarshaler()))

    mfs: ta.List[MarshalerFactory] = [  # noqa
        PRIMITIVE_MARSHALER_FACTORY,
        OptionalMarshalerFactory(),
        DataclassMarshalerFactory(),
        IterableMarshalerFactory(),
    ]

    mf: MarshalerFactory = SpecCacheFactory(  # noqa
        RecursiveMarshalerFactory(
            CompositeFactory(
                *mfs
            )
        )
    )

    mc = MarshalContext(factory=mf)
    for _ in range(2):
        print(mc.make(Foo).marshal(mc, Foo([420, 421], 'barf', Foo([1, 2], 'xxx'))))
    mc.make(ta.Optional[int]).marshal(mc, 420)
