import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..collection import DuplicateUniqueTypedValueError
from ..collection import TypedValues
from ..values import ScalarTypedValue
from ..values import TypedValue
from ..values import UniqueTypedValue


##


class GenerativeOption(TypedValue, lang.Abstract):
    pass


class TopK(GenerativeOption, UniqueTypedValue, ScalarTypedValue[int], lang.Final):
    pass


#


class ChatOption(TypedValue, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class ToolSpec(lang.Final):
    name: str
    params: ta.Sequence[ta.Any]

    _: dc.KW_ONLY

    desc: str


@dc.dataclass(frozen=True)
class Tool(ChatOption, lang.Final):
    spec: ToolSpec


#


class ResponseFormat(ChatOption, UniqueTypedValue, lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class TextResponseFormat(ResponseFormat, lang.Final):
    pass


TEXT_RESPONSE_FORMAT = TextResponseFormat()


@dc.dataclass(frozen=True)
class JsonResponseFormat(ResponseFormat, lang.Final):
    schema: ta.Any | None = None


JSON_RESPONSE_FORMAT = JsonResponseFormat()


##


def test_typed_values():
    foo_tool = ToolSpec('foo', [], desc='foo')
    bar_tool = ToolSpec('bar', [], desc='bar')

    assert list(TypedValues(
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool(foo_tool),
    )) == [
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool(foo_tool),
    ]

    assert list(TypedValues(
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
        TypedValues(
            TEXT_RESPONSE_FORMAT,
            JSON_RESPONSE_FORMAT,
        )
    except DuplicateUniqueTypedValueError as e:
        assert e == DuplicateUniqueTypedValueError(  # noqa
            ResponseFormat,
            JSON_RESPONSE_FORMAT,
            TEXT_RESPONSE_FORMAT,  # noqa
        )
    else:
        raise Exception('Did not raise!')  # noqa

    assert list(opts := TypedValues(
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

    assert list(TypedValues(*opts.without(ResponseFormat))) == [Tool(foo_tool), TopK(10), Tool(bar_tool)]
    assert list(TypedValues(*opts.without(Tool))) == [JSON_RESPONSE_FORMAT, TopK(10)]
