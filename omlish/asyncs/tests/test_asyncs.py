import asyncio
import concurrent.futures
import time

import pytest

from ... import asyncs as ay
from ... import iterators


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
            hello("Billy Bob", .3),
            hello("Billy Alice", .1),
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


def test_await_futures():
    def fn() -> float:
        time.sleep(.2)
        return time.time()

    tp: concurrent.futures.Executor
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as tp:
        futures = [tp.submit(fn) for _ in range(10)]
        assert not ay.await_futures(futures, tick_fn=iter([True, False]).__next__)
        assert ay.await_futures(futures)

    def pairs(l):
        return [set(p) for p in iterators.chunk(2, l)]

    idxs = [t[0] for t in sorted(list(enumerate(futures)), key=lambda t: t[1].result())]
    assert pairs(idxs) == pairs(range(10))


def test_syncable_iterable():
    async def f():
        return 1

    @ay.syncable_iterable
    async def g():
        yield await f()

    assert list(g()) == [1]
