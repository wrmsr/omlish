import pytest

from .. import properties as properties_
from .. import types as types_


def test_registries_property():
    class C:
        vals = properties_.property_()

        vals.registering('a')('C.a')
        vals.registering('b')('C.b')

    class D(C):

        C.vals.registering('c')('D.c')

    class E(D):

        D.vals.registering('a')('E.a')

    assert C().vals['a'] == 'C.a'
    assert C().vals['b'] == 'C.b'
    with pytest.raises(types_.NotRegisteredException):
        C().vals['c']

    assert D().vals['a'] == 'C.a'
    assert D().vals['b'] == 'C.b'
    assert D().vals['c'] == 'D.c'

    assert E().vals['c'] == 'D.c'
    assert E().vals['a'] == 'E.a'


def test_binding_registries_property():
    class C:
        fns = properties_.property_(bind=True)

        @fns.registering('a')
        def _a(self):
            return 0

        @fns.registering('b')
        def _b(self):
            return 1

    class D(C):

        @C.fns.registering('c')
        def _c(self):
            return 2

    class E(D):

        @D.fns.registering('a')
        def _a4(self):
            return 4

    assert C().fns['a']() == 0
    assert C().fns['b']() == 1
    with pytest.raises(types_.NotRegisteredException):
        C().fns['c']()

    assert D().fns['a']() == 0
    assert D().fns['b']() == 1
    assert D().fns['c']() == 2

    assert E().fns['c']() == 2
    assert E().fns['a']() == 4


def test_multi_registries_property():
    class C:
        vals = properties_.multi_property()

        vals.registering('a')(0)
        vals.registering('a')(1)
        vals.registering('b')(2)

    class D(C):

        C.vals.registering('a')(3)
        C.vals.registering('b')(4)

    class E(C):

        C.vals.registering('a')(5)
        C.vals.registering('b')(6)

    class F(D, E):

        C.vals.registering('a')(7)
        C.vals.registering('b')(8)

    assert C().vals['a'] == {0, 1}
    assert C().vals['b'] == {2}

    assert D().vals['a'] == {0, 1, 3}
    assert D().vals['b'] == {2, 4}

    assert E().vals['a'] == {0, 1, 5}
    assert E().vals['b'] == {2, 6}

    assert F().vals['a'] == {0, 1, 3, 5, 7}
    assert F().vals['b'] == {2, 4, 6, 8}
