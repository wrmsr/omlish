from ..chat import ResponseFormat  # noqa
from ..chat import TEXT_RESPONSE_FORMAT
from ..chat import Tool
from ..models import TopK
from ..options import Options
from ..tool import ToolParameters
from ..tool import ToolSpecification


def test_options():
    foo_tool = ToolSpecification('foo', 'foo', ToolParameters('str', {}, set()))
    bar_tool = ToolSpecification('bar', 'bar', ToolParameters('str', {}, set()))

    assert list(Options(
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool(foo_tool),
    )) == [
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool(foo_tool),
    ]

    assert list(Options(
        TopK(5),
        Tool(bar_tool),
        TEXT_RESPONSE_FORMAT,
        Tool(foo_tool),
    )) == [
        TopK(5),
        Tool(bar_tool),
        TEXT_RESPONSE_FORMAT,
        Tool(foo_tool),
    ]
