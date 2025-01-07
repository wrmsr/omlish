"""
FIXME:
 - sleeps -> barriers lol
 - pydevd_nest_asyncio._patch_loop(trai._async.TrioEventLoop) :|
  - trio_asyncio._base.BaseTrioEventLoop.call_soon ->
  - pydevd_nest_asyncio._PydevdAsyncioUtils.try_to_get_internal_callback(callback)
"""
import asyncio
import functools
import typing as ta

import anyio
import pytest
import sniffio
import trio

from ... import lang
from ...diag import pydevd as pdu
from ...testing import pytest as ptu
from ..asyncio import all as asu


if ta.TYPE_CHECKING:
    import trio_asyncio as trai
else:
    trai = lang.proxy_import('trio_asyncio')


@pytest.fixture(autouse=True)
def _patch_for_trio_asyncio_fixture():
    pdu.patch_for_trio_asyncio()


@ptu.skip.if_cant_import('trio_asyncio')
def test_hybrid():
    async def hybrid():
        await trio.sleep(.1)
        await asyncio.sleep(.1)
        print('Well, that worked')

    trai.run(trai.allow_asyncio, hybrid)


@ptu.skip.if_cant_import('trio_asyncio')
def test_asyncio_from_trio0():
    async def aio_sleep(sec=.1):
        await asyncio.sleep(sec)

    async def trio_sleep(sec=.2):
        await trai.aio_as_trio(aio_sleep)(sec)

    trai.run(trio_sleep, .3)


@ptu.skip.if_cant_import('trio_asyncio')
def test_asyncio_from_trio1():
    @trai.aio_as_trio
    async def trio_sleep(sec=.1):
        await asyncio.sleep(sec)

    trai.run(trio_sleep, .3)


@ptu.skip.if_cant_import('trio_asyncio')
def test_asyncio_from_trio2():
    async def aio_sleep(sec=.1):
        await asyncio.sleep(sec)

    async def trio_sleep(sec=.2):
        await trai.aio_as_trio(aio_sleep(sec))

    trai.run(trio_sleep, .3)


@ptu.skip.if_cant_import('trio_asyncio')
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


@ptu.skip.if_cant_import('trio_asyncio')
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


@ptu.skip.if_cant_import('trio_asyncio')
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
            print('within')
            await trai.aio_as_trio(ctx.delay)(.2)

    trai.run(trio_ctx)


@ptu.skip.if_cant_import('trio_asyncio')
def test_trio_from_asyncio0():
    async def trio_sleep(sec=.1):
        await trio.sleep(sec)

    async def aio_sleep(sec=.2):
        await trai.trio_as_aio(trio_sleep)(sec)

    trai.run(trai.aio_as_trio, functools.partial(aio_sleep, .3))


@ptu.skip.if_cant_import('trio_asyncio')
def test_trio_from_asyncio1():
    @trai.trio_as_aio
    async def aio_sleep(sec=.2):
        await trio.sleep(sec)

    trai.run(trai.aio_as_trio, functools.partial(aio_sleep, .3))


@ptu.skip.if_cant_import('trio_asyncio')
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


@ptu.skip.if_cant_import('trio_asyncio')
@pytest.mark.asyncs('trio')
async def test_trio_asyncio_loop(harness) -> None:
    async with trai.open_loop() as loop:  # noqa
        await trio.sleep(.1)
        await trai.aio_as_trio(asyncio.sleep)(.1)


@ptu.skip.if_cant_import('trio_asyncio')
@pytest.mark.asyncs
async def test_all_asyncs(__async_backend):  # noqa
    await anyio.sleep(.1)

    backend = sniffio.current_async_library()
    match __async_backend:
        case 'asyncio':
            assert backend == 'asyncio'
            assert asu.get_real_current_loop() is not None
            assert trai.current_loop.get() is None
            assert not isinstance(asyncio.get_running_loop(), trai.TrioEventLoop)

            await asyncio.sleep(.1)
            with pytest.raises(RuntimeError):
                await trio.sleep(.1)

        case 'trio':
            assert backend == 'trio'
            assert asu.get_real_current_loop() is None
            assert trai.current_loop.get() is None

            with pytest.raises(RuntimeError):
                await asyncio.sleep(.1)
            await trio.sleep(.1)

        case 'trio_asyncio':
            assert backend == 'asyncio'
            assert isinstance(asyncio.get_running_loop(), trai.TrioEventLoop)

            await asyncio.sleep(.1)
            with pytest.raises(RuntimeError):
                await trio.sleep(.1)

        case _:
            raise ValueError(__async_backend)


@ptu.skip.if_cant_import('trio_asyncio')
@pytest.mark.asyncs('trio_asyncio')
async def test_just_trio_asyncio(__async_backend):  # noqa
    assert __async_backend == 'trio_asyncio'
    backend = sniffio.current_async_library()
    assert backend == 'asyncio'
    assert isinstance(asyncio.get_running_loop(), trai.TrioEventLoop)

    await anyio.sleep(.1)


# FIXME: ???
# @ptu.skip.if_cant_import('trio_asyncio')
# @pytest.mark.asyncs('trio_asyncio')
# async def test_asyncio_no_loop():
#     backend = sniffio.current_async_library()
#     assert backend == 'asyncio'
#
#     assert trai.current_loop.get() is None
#
#     await anyio.sleep(.1)
