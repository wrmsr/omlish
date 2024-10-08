from omlish import marshal as msh

from ..marshal import MarshalContent


def test_marshal():
    assert msh.marshal('hi', MarshalContent) == 'hi'
