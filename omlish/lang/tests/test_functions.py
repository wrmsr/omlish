import pytest

from ..functions import Args
from ..functions import as_async
from ..functions import coalesce
from ..functions import finally_
from ..functions import opt_coalesce
from ..functions import try_


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


@pytest.mark.asyncio
async def test_as_async():
    assert (await as_async(lambda: 420)()) == 420


def test_coalesce():
    oi0: int | None = None
    oi1: int | None = 1

    #

    assert coalesce(oi0, 2) == 2
    assert coalesce(oi1, 2) == 1
    assert coalesce(oi0, oi1, 2) == 1

    with pytest.raises(ValueError):  # noqa
        assert coalesce(oi0, None)

    #

    assert opt_coalesce(oi0, 2) == 2
    assert opt_coalesce(oi1, 2) == 1
    assert opt_coalesce(oi0, oi1, 2) == 1
    assert opt_coalesce(oi0, None) is None
