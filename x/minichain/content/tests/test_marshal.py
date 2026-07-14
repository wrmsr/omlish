import uuid

import pytest

from omcore import dataclasses as dc
from omcore import marshal as msh

from ...content.placeholders import ContentPlaceholder
from ...content.placeholders import PlaceholderContent
from .._marshal import MarshalContent
from .._marshal import MarshalRawContent
from .._marshal import MarshalSingleRawContent
from ..containers import ConcatContent
from ..content import Content
from ..itemlist import ItemListContent
from ..json import JsonContent
from ..marshal import DisableDynamicClassMarshaling
from ..marshal import DynamicClassForbiddenMarshalError
from ..marshal import EnableDynamicClassUnmarshaling
from ..metadata import ContentUuid
from ..raw import RawContent
from ..raw import SingleRawContent
from ..text import TextContent


@dc.dataclass(frozen=True)
class Foo:
    c: Content


def test_marshal():
    for _ in range(2):
        assert msh.marshal('hi', MarshalContent) == 'hi'
        assert msh.marshal('hi', Content) == 'hi'
        assert msh.marshal(Foo('hi')) == {'c': 'hi'}

        assert msh.marshal(TextContent('hi'), Content) == {'text': {'s': 'hi'}}
        assert msh.marshal(ConcatContent(['hi', [TextContent('bye')]]), Content) == {'concat': {'l': ['hi', [{'text': {'s': 'bye'}}]]}}  # noqa

        u = uuid.uuid7()
        assert msh.marshal(TextContent('hi').with_metadata(ContentUuid(u)), Content) == {'text': {'s': 'hi', 'metadata': [{'content_uuid': str(u)}]}}  # noqa

        assert msh.marshal(JsonContent({'abc': 420}), Content) == {'json': {'v': {'abc': 420}}}

        assert msh.marshal(ItemListContent(['hi', 'there']), Content) == {'item_list': {'l': ['hi', 'there'], 'style': '-'}}  # noqa


@dc.dataclass(frozen=True)
class SingleRawFoo:
    c: SingleRawContent


def test_single_raw_marshal():
    assert msh.marshal('hi', MarshalSingleRawContent) == 'hi'
    assert msh.marshal('hi', SingleRawContent) == 'hi'
    assert msh.marshal(SingleRawFoo('hi')) == {'c': 'hi'}

    assert msh.marshal(TextContent('hi'), SingleRawContent) == {'text': {'s': 'hi'}}

    u = uuid.uuid7()
    assert msh.marshal(TextContent('hi').with_metadata(ContentUuid(u)), SingleRawContent) == {'text': {'s': 'hi', 'metadata': [{'content_uuid': str(u)}]}}  # noqa


@dc.dataclass(frozen=True)
class RawFoo:
    c: RawContent


def test_raw_marshal():
    assert msh.marshal('hi', MarshalRawContent) == 'hi'
    assert msh.marshal('hi', RawContent) == 'hi'
    assert msh.marshal(RawFoo('hi')) == {'c': 'hi'}

    assert msh.marshal(TextContent('hi'), RawContent) == {'text': {'s': 'hi'}}
    assert msh.marshal([TextContent('hi'), 'bye'], RawContent) == [{'text': {'s': 'hi'}}, 'bye']

    u = uuid.uuid7()
    assert msh.marshal(TextContent('hi').with_metadata(ContentUuid(u)), RawContent) == {'text': {'s': 'hi', 'metadata': [{'content_uuid': str(u)}]}}  # noqa


class FooPlaceholder(ContentPlaceholder):
    pass


def test_placeholder():
    c = PlaceholderContent('foo')
    with pytest.raises(DynamicClassForbiddenMarshalError):
        msh.marshal(c, Content, DisableDynamicClassMarshaling())
    m = msh.marshal(c, Content)
    print(m)
    with pytest.raises(DynamicClassForbiddenMarshalError):
        msh.unmarshal(m, Content)
    c2 = msh.unmarshal(m, Content, EnableDynamicClassUnmarshaling())
    print(c2)
    assert c == c2

    c = PlaceholderContent(FooPlaceholder)
    m = msh.marshal(c, Content)
    print(m)
    c2 = msh.unmarshal(m, Content, EnableDynamicClassUnmarshaling())
    print(c2)
    assert c == c2
