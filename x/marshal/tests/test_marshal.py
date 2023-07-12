from ..base import MarshalContext
from ..exc import UnhandledSpecException
from ..primitives import PrimitiveMarshaler


def test_marshal():
    v = PrimitiveMarshaler()(MarshalContext(), 420)
    print(v)

    try:
        PrimitiveMarshaler()(MarshalContext(), object())
    except UnhandledSpecException as e:
        assert e.spec is object
    else:
        assert False
