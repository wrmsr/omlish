"""
FIXME:
 - pydevd_nest_asyncio._patch_loop(trai._async.TrioEventLoop) :|
  - trio_asyncio._base.BaseTrioEventLoop.call_soon ->
  - pydevd_nest_asyncio._PydevdAsyncioUtils.try_to_get_internal_callback(callback)
"""
import asyncio
import functools
import typing as ta

import pytest
import trio

from ... import lang
from ...testing import pydevd as pdu
from ...testing.pytest import skip_if_cant_import

if ta.TYPE_CHECKING:
    import trio_asyncio as trai
else:
    trai = lang.proxy_import('trio_asyncio')


@pytest.fixture(autouse=True)
def patch_for_trio_asyncio_fixture():
    pdu.patch_for_trio_asyncio()


@skip_if_cant_import('trio_asyncio')
def test_hybrid():
    async def hybrid():
        await trio.sleep(.1)
        await asyncio.sleep(.1)
        print("Well, that worked")

    trai.run(trai.allow_asyncio, hybrid)


@skip_if_cant_import('trio_asyncio')
def test_asyncio_from_trio0():
    async def aio_sleep(sec=.1):
        await asyncio.sleep(sec)

    async def trio_sleep(sec=.2):
        await trai.aio_as_trio(aio_sleep)(sec)

    trai.run(trio_sleep, .3)


@skip_if_cant_import('trio_asyncio')
def test_asyncio_from_trio1():
    @trai.aio_as_trio
    async def trio_sleep(sec=.1):
        await asyncio.sleep(sec)

    trai.run(trio_sleep, .3)


@skip_if_cant_import('trio_asyncio')
def test_asyncio_from_trio2():
    async def aio_sleep(sec=.1):
        await asyncio.sleep(sec)

    async def trio_sleep(sec=.2):
        await trai.aio_as_trio(aio_sleep(sec))

    trai.run(trio_sleep, .3)


@skip_if_cant_import('trio_asyncio')
def test_asyncio_from_trio3():
    async def aio_sleep(sec=.1):
        await asyncio.sleep(sec)
        return 42

    async def trio_sleep(sec=2):
        f = aio_sleep(.1)
        f = asyncio.ensure_future(f)
        r = await trai.aio_as_trio(f)
        assert r == 42

    trai.run(trio_sleep, .3)


@skip_if_cant_import('trio_asyncio')
def test_asyncio_from_trio4():
    async def aio_slow():
        n = 0.
        for _ in range(3):
            await asyncio.sleep(n)
            yield n
            n += .1

    async def printer():
        async for n in trai.aio_as_trio(aio_slow()):
            print(n)

    trai.run(printer)


@skip_if_cant_import('trio_asyncio')
def test_asyncio_from_trio5():
    class AsyncCtx:
        async def __aenter__(self):
            await asyncio.sleep(.1)
            return self

        async def __aexit__(self, *tb):
            await asyncio.sleep(.1)

        async def delay(self, sec=.1):
            await asyncio.sleep(sec)

    async def trio_ctx():
        async with trai.aio_as_trio(AsyncCtx()) as ctx:
            print("within")
            await trai.aio_as_trio(ctx.delay)(.2)

    trai.run(trio_ctx)


@skip_if_cant_import('trio_asyncio')
def test_trio_from_asyncio0():
    async def trio_sleep(sec=.1):
        await trio.sleep(sec)

    async def aio_sleep(sec=.2):
        await trai.trio_as_aio(trio_sleep)(sec)

    trai.run(trai.aio_as_trio, functools.partial(aio_sleep, .3))


@skip_if_cant_import('trio_asyncio')
def test_trio_from_asyncio1():
    @trai.trio_as_aio
    async def aio_sleep(sec=.2):
        await trio.sleep(sec)

    trai.run(trai.aio_as_trio, functools.partial(aio_sleep, .3))


@skip_if_cant_import('trio_asyncio')
def test_trio_from_asyncio2():
    async def trio_sleep(sec=.1):
        await trio.sleep(sec)
        return 42

    def cb(f):
        assert f.result() == 42

    async def aio_sleep(sec=.2):
        f = trai.trio_as_aio(trio_sleep)(.1)
        f.add_done_callback(cb)
        r = await f
        assert r == 42

    trai.run(trai.aio_as_trio, functools.partial(aio_sleep, .3))
