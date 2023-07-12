from ..base import MarshalContext
from ..primitives import PrimitiveMarshaler


def test_marshal():
    v = PrimitiveMarshaler()(MarshalContext(), 420)
    print(v)
