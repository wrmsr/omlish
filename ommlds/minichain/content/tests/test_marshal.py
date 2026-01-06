import uuid

from omlish import dataclasses as dc
from omlish import marshal as msh

from ...metadata import Uuid
from .._marshal import MarshalContent
from .._marshal import MarshalRawContent
from .._marshal import MarshalSingleRawContent
from ..content import Content
from ..raw import RawContent
from ..raw import SingleRawContent
from ..sequence import InlineContent
from ..text import TextContent


@dc.dataclass(frozen=True)
class Foo:
    c: Content


def test_marshal():
    assert msh.marshal('hi', MarshalContent) == 'hi'
    assert msh.marshal('hi', Content) == 'hi'
    assert msh.marshal(Foo('hi')) == {'c': 'hi'}

    assert msh.marshal(TextContent('hi'), Content) == {'text': {'s': 'hi'}}
    assert msh.marshal(InlineContent(['hi', [TextContent('bye')]]), Content) == {'inline': {'l': ['hi', [{'text': {'s': 'bye'}}]]}}  # noqa

    u = uuid.uuid4()
    assert msh.marshal(TextContent('hi').with_metadata(Uuid(u)), Content) == {'text': {'s': 'hi', 'metadata': [{'uuid': str(u)}]}}  # noqa


@dc.dataclass(frozen=True)
class SingleRawFoo:
    c: SingleRawContent


def test_single_raw_marshal():
    assert msh.marshal('hi', MarshalSingleRawContent) == 'hi'
    assert msh.marshal('hi', SingleRawContent) == 'hi'
    assert msh.marshal(SingleRawFoo('hi')) == {'c': 'hi'}

    assert msh.marshal(TextContent('hi'), SingleRawContent) == {'text': {'s': 'hi'}}

    u = uuid.uuid4()
    assert msh.marshal(TextContent('hi').with_metadata(Uuid(u)), SingleRawContent) == {'text': {'s': 'hi', 'metadata': [{'uuid': str(u)}]}}  # noqa


@dc.dataclass(frozen=True)
class RawFoo:
    c: RawContent


def test_raw_marshal():
    assert msh.marshal('hi', MarshalRawContent) == 'hi'
    assert msh.marshal('hi', RawContent) == 'hi'
    assert msh.marshal(RawFoo('hi')) == {'c': 'hi'}

    assert msh.marshal(TextContent('hi'), RawContent) == {'text': {'s': 'hi'}}
    assert msh.marshal([TextContent('hi'), 'bye'], RawContent) == [{'text': {'s': 'hi'}}, 'bye']

    u = uuid.uuid4()
    assert msh.marshal(TextContent('hi').with_metadata(Uuid(u)), RawContent) == {'text': {'s': 'hi', 'metadata': [{'uuid': str(u)}]}}  # noqa
