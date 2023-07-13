import typing as ta

from ..base import MarshalContext
from ..base import Marshaler
from ..base import MarshalerFactory
from ..base import RecursiveMarshalerFactory
from ..base import SetType
from ..exc import UnhandledSpecException
from ..factories import CompositeFactory
from ..factories import RecursiveSpecFactory
from ..factories import SpecCacheFactory
from ..factories import SpecMapFactory
from ..primitives import PrimitiveMarshaler
from ..registries import Registry
from ..specs import Spec
from ..specs import spec_of


def test_marshal():
    v = PrimitiveMarshaler().marshal(MarshalContext(), 420)
    print(v)

    try:
        PrimitiveMarshaler().marshal(MarshalContext(), object())
    except UnhandledSpecException as e:
        assert e.spec is object
    else:
        assert False

    reg = Registry()
    reg.register(spec_of(int), SetType(marshaler=PrimitiveMarshaler()))

    mfs: ta.List[MarshalerFactory] = [  # noqa
        SpecMapFactory({
            int: PrimitiveMarshaler(),
        }),
    ]

    mf: MarshalerFactory = SpecCacheFactory(  # noqa
        RecursiveMarshalerFactory(
            CompositeFactory(
                *mfs
            )
        )
    )

    mc = MarshalContext()
    m = mf(mc, int)
    print(m.marshal(mc, 421))
