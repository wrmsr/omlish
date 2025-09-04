import asyncio
import contextlib

import pytest

from ..asyncs import as_async
from ..asyncs import async_list
from ..asyncs import sync_await


@pytest.mark.asyncs('asyncio')
async def test_as_async():
    assert (await as_async(lambda: 420)()) == 420


@pytest.mark.asyncs('asyncio')
async def test_async_list():
    async def barf(x):
        yield x
        await asyncio.sleep(.01)
        yield x + 1

    assert await async_list(barf(3)) == [3, 4]


def test_sync_await():
    c = 0

    def inc():
        nonlocal c
        c += 1
        return c

    #

    async def f1():
        return inc()

    assert sync_await(f1()) == 1

    async def f2():
        await f1()
        return inc()

    assert sync_await(f2()) == 3

    #

    @contextlib.asynccontextmanager
    async def acm():
        await f1()
        try:
            yield
        finally:
            await f1()

    async def f3():
        async with acm():
            return inc()

    assert sync_await(f3()) == 5
    assert c == 6

    #

    async def ag():
        try:
            await f2()
            yield inc()
            await f2()
            yield inc()
            await f2()
        finally:
            await f2()

    async def ai(exc=None):
        l = []
        async for i in ag():
            l.append(i)
            if exc is not None:
                raise exc(l)
        return l

    assert sync_await(ai()) == [9, 12]
    assert c == 16

    #

    class FooError(Exception):
        pass

    with pytest.raises(FooError) as ex:
        sync_await(ai(FooError))

    assert ex.value.args[0] == [19]
    assert c == 21
