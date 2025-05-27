from ..types import NULL_PRIMITIVE_TYPE
from ..types import Primitive


def test_simple_eq():
    assert Primitive('null') == NULL_PRIMITIVE_TYPE
