from ..types import NULL_PRIMITIVE_TOOL_DTYPE
from ..types import PrimitiveToolDtype
from ..types import ToolSpec


def test_tool_specs():
    assert ToolSpec('foo').name == 'foo'


def test_simple_eq():
    assert PrimitiveToolDtype('null') == NULL_PRIMITIVE_TOOL_DTYPE
