from ..base import MarshalContext
from ..base import SetType
from ..exc import UnhandledSpecException
from ..primitives import PrimitiveMarshaler
from ..registries import Registry
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
