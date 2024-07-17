import asyncio

import pytest

from ... import asyncs as ay


@pytest.mark.asyncio
async def test_simple():
    l = []

    async def f(sleepfor) -> int:
        await asyncio.sleep(sleepfor)
        return 4

    async def hello(name, sleepfor) -> int:
        l.append(f'start {name}')
        x = await f(sleepfor)
        l.append(f'end {name}')
        return x

    async def main():
        await asyncio.gather(
            hello('Billy Bob', .3),
            hello('Billy Alice', .1),
        )

    await main()


def test_sync_await():
    async def f1():
        return 1

    assert ay.sync_await(f1) == 1

    async def f2():
        await f1()
        return 2

    assert ay.sync_await(f2) == 2


def test_syncable_iterable():
    async def f():
        return 1

    @ay.syncable_iterable
    async def g():
        yield await f()

    assert list(g()) == [1]
