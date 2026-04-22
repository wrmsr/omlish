import typing as ta

import pytest

from ... import check
from ... import dataclasses as dc
from ... import lang
from ..collection import DuplicateUniqueTypedValueError
from ..collection import TypedValues
from ..scalars import ScalarTypedValue
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
class Tool(ChatOption, lang.Final):
    name: str


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
    assert list(TypedValues[GenerativeOption | ChatOption](
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool('foo'),
    )) == [
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool('foo'),
    ]

    assert list(TypedValues[GenerativeOption | ChatOption](
        TopK(5),
        Tool('bar'),
        TEXT_RESPONSE_FORMAT,
        Tool('foo'),
    )) == [
        TopK(5),
        Tool('bar'),
        TEXT_RESPONSE_FORMAT,
        Tool('foo'),
    ]

    with pytest.raises(DuplicateUniqueTypedValueError) as e:
        TypedValues[GenerativeOption | ChatOption](
            TEXT_RESPONSE_FORMAT,
            JSON_RESPONSE_FORMAT,
        )
    assert e.value == DuplicateUniqueTypedValueError(  # noqa
        ResponseFormat,
        JSON_RESPONSE_FORMAT,
        TEXT_RESPONSE_FORMAT,  # noqa
    )

    assert list(opts := TypedValues[GenerativeOption | ChatOption](
        TopK(5),
        TEXT_RESPONSE_FORMAT,
        Tool('foo'),
        JSON_RESPONSE_FORMAT,
        TopK(10),
        Tool('bar'),
        override=True,
    )) == [
        Tool('foo'),
        JSON_RESPONSE_FORMAT,
        TopK(10),
        Tool('bar'),
    ]

    assert opts[TopK] == TopK(10)
    assert list(opts[Tool]) == [Tool('foo'), Tool('bar')]
    assert opts[ResponseFormat] == JSON_RESPONSE_FORMAT
    assert opts[JsonResponseFormat] == JSON_RESPONSE_FORMAT
    assert opts.get_any(JsonResponseFormat) == (JSON_RESPONSE_FORMAT,)

    assert ResponseFormat in opts
    assert JsonResponseFormat in opts
    assert ResponseFormat in opts.keys()  # noqa
    assert JsonResponseFormat not in opts.keys()  # noqa

    assert list(TypedValues(*opts.without(ResponseFormat))) == [Tool('foo'), TopK(10), Tool('bar')]
    assert list(TypedValues(*opts.without(Tool))) == [JSON_RESPONSE_FORMAT, TopK(10)]
    assert list(TypedValues(*opts.update(discard=[Tool]))) == [JSON_RESPONSE_FORMAT, TopK(10)]


def test_mro_check():
    class Good(ScalarTypedValue[int], UniqueTypedValue):
        pass

    assert Good(5).v == 5
    assert issubclass(Good, UniqueTypedValue)

    with pytest.raises(TypeError):  # noqa
        class Bad(UniqueTypedValue, ScalarTypedValue[int]):
            pass


def test_get():
    assert check.not_none(TypedValues(TopK(10)).get(TopK)).v == 10
    assert TypedValues().get(TopK) is None
    assert TypedValues().get(TopK(11)).v == 11


def test_get_any():
    TypedValues(TopK(10)).get_any(lang.Abstract)


def test_bool():
    with pytest.raises(TypeError):  # noqa
        bool(TopK(0))  # noqa


def test_a_ton():
    tv_cls_lst: list = []
    tv_lst: list = []

    class UniqueFoo(UniqueTypedValue, lang.Abstract):
        pass

    for i in range(1500):
        bcs: list
        match i % 3:
            case 0:
                bcs = [ScalarTypedValue[int], UniqueFoo]
            case 1:
                bcs = [ScalarTypedValue[int]]
            case _:
                bcs = [TypedValue]
        tv_cls = lang.new_type(f'Foo{i}', tuple(bcs), {})  # noqa
        tv_cls_lst.append(tv_cls)
        if issubclass(tv_cls, ScalarTypedValue):
            tv_lst.append(tv_cls(i))
        else:
            tv_lst.append(tv_cls())

    tvc = TypedValues(*tv_lst, override=True)
    assert len(tvc) == 1001
    assert tvc[UniqueFoo] == tv_cls_lst[1497](1497)


def test_update():
    assert list(TypedValues(Tool('foo')).update(Tool('bar'))) == [Tool('foo'), Tool('bar')]
    assert list(TypedValues(Tool('foo')).update(Tool('bar'), mode='prepend')) == [Tool('bar'), Tool('foo')]
    with pytest.raises(DuplicateUniqueTypedValueError):
        TypedValues(Tool('foo'), TEXT_RESPONSE_FORMAT).update(JSON_RESPONSE_FORMAT)  # noqa
    assert list(TypedValues(Tool('foo'), TEXT_RESPONSE_FORMAT).update(JSON_RESPONSE_FORMAT, mode='override')) == [Tool('foo'), JSON_RESPONSE_FORMAT]  # noqa
    assert list(TypedValues(Tool('foo'), TEXT_RESPONSE_FORMAT).update(JSON_RESPONSE_FORMAT, mode='default')) == [Tool('foo'), TEXT_RESPONSE_FORMAT]  # noqa
    assert list(TypedValues[ChatOption](Tool('foo')).update(JSON_RESPONSE_FORMAT, mode='default')) == [JSON_RESPONSE_FORMAT, Tool('foo')]  # noqa
