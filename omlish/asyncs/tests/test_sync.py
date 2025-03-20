from ..sync import sync_await
from ..sync import syncable_iterable


def test_sync_await():
    async def f1():
        return 1

    assert sync_await(f1) == 1

    async def f2():
        await f1()
        return 2

    assert sync_await(f2) == 2


def test_syncable_iterable():
    async def f():
        return 1

    @syncable_iterable
    async def g():
        yield await f()

    assert list(g()) == [1]
