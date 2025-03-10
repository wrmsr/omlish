from ..chat.formats import JSON_RESPONSE_FORMAT
from ..chat.formats import TEXT_RESPONSE_FORMAT
from ..chat.formats import JsonResponseFormat
from ..chat.formats import ResponseFormat
from ..chat.tools import Tool
from ..chat.tools import ToolSpec
from ..generative import TopK
from ..options import DuplicateUniqueOptionError
from ..options import Options


def test_options():
    foo_tool = ToolSpec('foo', [], desc='foo')
    bar_tool = ToolSpec('bar', [], desc='bar')

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

    try:
        Options(
            TEXT_RESPONSE_FORMAT,
            JSON_RESPONSE_FORMAT,
        )
    except DuplicateUniqueOptionError as e:
        assert e == DuplicateUniqueOptionError(ResponseFormat, JSON_RESPONSE_FORMAT, TEXT_RESPONSE_FORMAT)  # noqa
    else:
        raise Exception('Did not raise!')  # noqa

    assert list(opts := Options(
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool(foo_tool),
        JSON_RESPONSE_FORMAT,
        TopK(10),
        Tool(bar_tool),
        override=True,
    )) == [
        Tool(foo_tool),
        JSON_RESPONSE_FORMAT,
        TopK(10),
        Tool(bar_tool),
    ]

    assert opts[TopK] == TopK(10)
    assert opts[Tool] == [Tool(foo_tool), Tool(bar_tool)]
    assert opts[ResponseFormat] == JSON_RESPONSE_FORMAT
    assert opts[JsonResponseFormat] == JSON_RESPONSE_FORMAT

    assert list(Options(*opts.without(ResponseFormat))) == [Tool(foo_tool), TopK(10), Tool(bar_tool)]
    assert list(Options(*opts.without(Tool))) == [JSON_RESPONSE_FORMAT, TopK(10)]
