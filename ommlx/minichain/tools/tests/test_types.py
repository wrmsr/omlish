from ..types import NULL_PRIMITIVE_TOOL_DTYPE
from ..types import PrimitiveToolDtype


def test_simple_eq():
    assert PrimitiveToolDtype('null') == NULL_PRIMITIVE_TOOL_DTYPE
