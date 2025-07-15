import uuid

from omlish import dataclasses as dc
from omlish import marshal as msh

from ....metadata import Uuid
from .._marshal import MarshalCanContent
from ...list import ListContent
from ...text import TextContent
from ..materialize import CanContent


@dc.dataclass(frozen=True)
class Foo:
    c: CanContent


def test_marshal():
    assert msh.marshal('hi', MarshalCanContent) == 'hi'
    assert msh.marshal('hi', CanContent) == 'hi'
    assert msh.marshal(Foo('hi')) == {'c': 'hi'}

    assert msh.marshal(TextContent('hi'), CanContent) == {'text': {'s': 'hi'}}
    assert msh.marshal(ListContent(['hi', [TextContent('bye')]]), CanContent) == {'list': {'l': ['hi', [{'text': {'s': 'bye'}}]]}}  # noqa

    u = uuid.uuid4()
    assert msh.marshal(TextContent('hi').with_metadata(Uuid(u)), CanContent) == {'text': {'s': 'hi', 'metadata': [{'uuid': str(u)}]}}  # noqa
