import pytest

from ..namespaces import GenericNamespaceMeta
from ..namespaces import Namespace


def test_namespace():
    class Foo(Namespace):
        X = 1
        Y = '2'

    with pytest.raises(TypeError):
        Foo()

    assert list(Foo) == [('X', 1), ('Y', '2')]
    assert Foo['X'] == 1


class Foos(Namespace):
    x = 1
    y = 2


class IntNamespaceMeta(GenericNamespaceMeta[int], check_values=int):
    pass


class IntNamespace(metaclass=IntNamespaceMeta):
    pass


class Bars(IntNamespace):
    x = 1
    y = 2


class CiBars2(IntNamespace, case_insensitive=True):
    x = 1
    Y = 2


class CiIntNamespaceMeta(GenericNamespaceMeta[int], check_values=int, case_insensitive=True):
    pass


class CiIntNamespace(metaclass=CiIntNamespaceMeta):
    pass


class CiBars(CiIntNamespace):
    x = 1
    Y = 2


def test_generic_namespaces():
    assert dict(Foos) == {'x': 1, 'y': 2}
    assert dict(Bars) == {'x': 1, 'y': 2}
    assert dict(CiBars) == {'x': 1, 'Y': 2}
    assert dict(CiBars2) == {'x': 1, 'Y': 2}

    with pytest.raises(TypeError):  # noqa
        class BadBars(IntNamespace):  # noqa
            x = 1
            y = 'banana'

    assert Bars['y'] == 2
    with pytest.raises(KeyError):
        Bars['Y']  # noqa
    assert CiBars['y'] == 2
    assert CiBars['Y'] == 2
    assert CiBars2['y'] == 2
    assert CiBars2['Y'] == 2
