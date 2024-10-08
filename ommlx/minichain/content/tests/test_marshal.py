from omlish import marshal as msh

from ..content import Content


def test_marshal():
    assert msh.marshal('hi', Content) == 'hi'
