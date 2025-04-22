import typing as ta

import pytest

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


class TopK(GenerativeOption, ScalarTypedValue[int], UniqueTypedValue, lang.Final):
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
    assert list(opts[Tool]) == [Tool(foo_tool), Tool(bar_tool)]
    assert opts[ResponseFormat] == JSON_RESPONSE_FORMAT
    assert opts[JsonResponseFormat] == JSON_RESPONSE_FORMAT
    assert opts.get_any(JsonResponseFormat) == (JSON_RESPONSE_FORMAT,)

    assert ResponseFormat in opts
    assert JsonResponseFormat in opts
    assert ResponseFormat in opts.keys()  # noqa
    assert JsonResponseFormat not in opts.keys()  # noqa

    assert list(TypedValues(*opts.without(ResponseFormat))) == [Tool(foo_tool), TopK(10), Tool(bar_tool)]
    assert list(TypedValues(*opts.without(Tool))) == [JSON_RESPONSE_FORMAT, TopK(10)]


def test_mro_check():
    class Good(ScalarTypedValue[int], UniqueTypedValue):
        pass

    assert Good(5).v == 5
    assert issubclass(Good, UniqueTypedValue)

    with pytest.raises(TypeError):  # noqa
        class Bad(UniqueTypedValue, ScalarTypedValue[int]):
            pass


def test_empty():
    assert TypedValues() is TypedValues()


def test_get_any():
    TypedValues(TopK(10)).get_any(lang.Abstract)
