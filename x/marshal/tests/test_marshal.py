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
from ..primitives import PRIMITIVE_MARSHALER_FACTORY
from ..primitives import PRIMITIVE_MARSHALER
from ..registries import Registry
from ..specs import Spec
from ..specs import spec_of


@dc.dataclass(frozen=True)
class Foo:
    il: list[int]
    s: str


def test_marshal():
    # reg = Registry()
    # reg.register(spec_of(int), SetType(marshaler=PrimitiveMarshaler()))

    mfs: ta.List[MarshalerFactory] = [  # noqa
        PRIMITIVE_MARSHALER_FACTORY,
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
    print(mc.make(Foo).marshal(mc, Foo([420, 421], 'barf')))
