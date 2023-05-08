import pytest

from .. import objects as objects_


def test_new_type():
    C = objects_.new_type('C', (object,), {'f': lambda self: 420})
    assert C().f() == 420


def test_simple_proxy():
    class WrappedInt(objects_.SimpleProxy):
        __wrapped_attrs__ = {'__add__'}

    assert WrappedInt(4) + 2 == 6

    class IncInt(objects_.SimpleProxy):

        def __add__(self, other):
            return self.__wrapped__.__add__(other + 1)

    assert IncInt(4) + 2 == 7


def test_no_bool():
    @objects_.no_bool
    def f():
        return 1

    assert f() == 1
    assert bool(f())
    with pytest.raises(TypeError):
        bool(f)

    class C(objects_.NoBool):
        pass

    assert C
    with pytest.raises(TypeError):
        bool(C())
