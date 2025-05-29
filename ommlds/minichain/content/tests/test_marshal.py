from omlish import dataclasses as dc
from omlish import marshal as msh

from ..content import Content
from ..marshal import MarshalContent


@dc.dataclass(frozen=True)
class Foo:
    c: Content


def test_marshal():
    assert msh.marshal('hi', MarshalContent) == 'hi'
    assert msh.marshal('hi', Content) == 'hi'  # type: ignore
    assert msh.marshal(Foo('hi')) == {'c': 'hi'}
