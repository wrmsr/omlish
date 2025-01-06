import asyncio
import typing as ta

import anyio
import pytest
import sniffio
import trio

from ... import lang
from ...diag import pydevd as pdu
from ...testing import pytest as ptu
from .. import flavors


if ta.TYPE_CHECKING:
    import trio_asyncio
else:
    trio_asyncio = lang.proxy_import('trio_asyncio')


##


@pytest.fixture(autouse=True)
def _patch_for_trio_asyncio_fixture():
    pdu.patch_for_trio_asyncio()


##


@flavors.mark_anyio
async def _anyio_func(call_asyncio, call_trio):
    await anyio.sleep(0)
    if call_asyncio:
        await flavors.from_asyncio(asyncio.sleep)(0)
        await flavors.adapt(asyncio.sleep)(0)
    if call_trio:
        await flavors.from_trio(trio.sleep)(0)
        await flavors.adapt(trio.sleep)(0)


@flavors.mark_asyncio
async def _asyncio_func(cross):
    assert sniffio.current_async_library() == 'asyncio'

    await anyio.sleep(0)
    await asyncio.sleep(0)
    if cross:
        await trio_asyncio.trio_as_aio(trio.sleep)(0)


@flavors.mark_trio
async def _trio_func(cross):
    assert sniffio.current_async_library() == 'trio'

    await anyio.sleep(0)
    if cross:
        await trio_asyncio.aio_as_trio(asyncio.sleep)(0)
    await trio.sleep(0)  # noqa


##


@ptu.skip.if_cant_import('trio_asyncio')
@pytest.mark.asyncs('asyncio')
async def test_asyncio_loop(harness) -> None:
    await _anyio_func(True, False)
    await _asyncio_func(False)

    # async with trio_asyncio.open_loop() as loop:  # noqa
    #     await _anyio_func(True, True)
    #     await _asyncio_func(True)
    #     await trio_asyncio.trio_as_aio(_trio_func)(True)


@ptu.skip.if_cant_import('trio_asyncio')
@pytest.mark.asyncs('trio')
async def test_trio_loop(harness) -> None:
    await _anyio_func(False, True)
    await _trio_func(False)

    async with trio_asyncio.open_loop():
        await _anyio_func(True, True)
        await trio_asyncio.aio_as_trio(_asyncio_func)(True)
        await _trio_func(True)


##


def test_get_flavor_anyio():
    assert flavors.get_flavor(anyio.sleep) == flavors.Flavor.ANYIO


def test_get_flavor_asyncio():
    assert flavors.get_flavor(asyncio.sleep) == flavors.Flavor.ASYNCIO


def test_get_flavor_trio():
    assert flavors.get_flavor(trio.sleep) == flavors.Flavor.TRIO
