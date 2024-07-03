import asyncio

import trio_asyncio as trai


def test_asyncio_from_trio():
    async def aio_sleep(sec=1):
        await asyncio.sleep(sec)

    async def trio_sleep(sec=2):
        await trai.aio_as_trio(aio_sleep)(sec)

    trai.run(trio_sleep, 3)

    #

    @trai.aio_as_trio
    async def trio_sleep(sec=1):
        await asyncio.sleep(sec)

    trai.run(trio_sleep, 3)

    #

    async def aio_sleep(sec=1):
        await asyncio.sleep(sec)

    async def trio_sleep(sec=2):
        await trai.aio_as_trio(aio_sleep(sec))

    trai.run(trio_sleep, 3)

    #

    async def aio_sleep(sec=1):
        await asyncio.sleep(sec)
        return 42

    async def trio_sleep(sec=2):
        f = aio_sleep(1)
        f = asyncio.ensure_future(f)
        r = await trai.aio_as_trio(f)
        assert r == 42

    trai.run(trio_sleep, 3)

    #

    async def aio_slow():
        n = 0
        while True:
            await asyncio.sleep(n)
            yield n
            n += 1

    async def printer():
        async for n in trai.aio_as_trio(aio_slow()):
            print(n)

    trai.run(printer)

    #

    class AsyncCtx:
        async def __aenter__(self):
            await asyncio.sleep(1)
            return self

        async def __aexit__(self, *tb):
            await asyncio.sleep(1)

        async def delay(self, sec=1):
            await asyncio.sleep(sec)

    async def trio_ctx():
        async with trai.aio_as_trio(AsyncCtx()) as ctx:
            print("within")
            await trai.aio_as_trio(ctx.delay)(2)

    trai.run(trio_ctx)
