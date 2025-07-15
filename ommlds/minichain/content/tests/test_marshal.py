import uuid

from omlish import dataclasses as dc
from omlish import marshal as msh

from ...metadata import Uuid
from .._marshal import MarshalCanContent
from .._marshal import MarshalContent
from ..materialize import CanContent
from ..sequence import InlineContent
from ..text import TextContent
from ..types import Content


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
class CcFoo:
    c: CanContent


def test_cc_marshal():
    assert msh.marshal('hi', MarshalCanContent) == 'hi'
    assert msh.marshal('hi', CanContent) == 'hi'
    assert msh.marshal(CcFoo('hi')) == {'c': 'hi'}

    assert msh.marshal(TextContent('hi'), CanContent) == {'text': {'s': 'hi'}}
    assert msh.marshal(InlineContent(['hi', [TextContent('bye')]]), CanContent) == {'inline': {'l': ['hi', [{'text': {'s': 'bye'}}]]}}  # noqa

    u = uuid.uuid4()
    assert msh.marshal(TextContent('hi').with_metadata(Uuid(u)), CanContent) == {'text': {'s': 'hi', 'metadata': [{'uuid': str(u)}]}}  # noqa
