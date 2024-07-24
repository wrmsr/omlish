import pytest

from ..functions import Args
from ..functions import try_
from ..functions import finally_


def test_args():
    def f(x, y, z):
        return x + y * z

    assert Args(1, 2, 3)(f) == 7


class FooError(Exception):
    pass


def test_try():
    def foo():
        raise FooError

    assert try_(foo, FooError, 5)() == 5


def test_finally():
    c = 0

    def foo():
        raise FooError

    def fin():
        nonlocal c
        c += 1

    f = finally_(foo, fin)
    with pytest.raises(FooError):
        f()
    assert c == 1
