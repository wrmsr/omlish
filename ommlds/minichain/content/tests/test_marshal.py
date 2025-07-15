import uuid

from omlish import dataclasses as dc
from omlish import marshal as msh

from ...metadata import Uuid
from .._marshal import MarshalContent
from ..list import ListContent
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
    assert msh.marshal(ListContent(['hi', [TextContent('bye')]]), Content) == {'list': {'l': ['hi', [{'text': {'s': 'bye'}}]]}}  # noqa

    u = uuid.uuid4()
    assert msh.marshal(TextContent('hi').with_metadata(Uuid(u)), Content) == {'text': {'s': 'hi', 'metadata': [{'uuid': str(u)}]}}  # noqa
