import pytest

from ..namespaces import Namespace


def test_namespace():
    class Foo(Namespace):
        X = 1
        Y = '2'

    with pytest.raises(TypeError):
        Foo()

    assert list(Foo) == [('X', 1), ('Y', '2')]
    assert Foo['X'] == 1
