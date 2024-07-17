from ..objects import SimpleProxy


def test_simple_proxy():
    class WrappedInt(SimpleProxy):
        __wrapped_attrs__ = ('__add__',)

    assert WrappedInt(4) + 2 == 6  # type: ignore

    class IncInt(SimpleProxy):
        def __add__(self, other):
            return self.__wrapped__.__add__(other + 1)

    assert IncInt(4) + 2 == 7
