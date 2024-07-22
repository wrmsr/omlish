import asyncio
import typing as ta

import anyio
import pytest
import sniffio
import trio

from .. import flavors
from ... import lang
from ...testing import pydevd as pdu
from ...testing.pytest import skip_if_cant_import

if ta.TYPE_CHECKING:
    import trio_asyncio as trio_asyncio
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
    if call_trio:
        await flavors.from_trio(trio.sleep)(0)


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
    await trio.sleep(0)


##


@skip_if_cant_import('trio_asyncio')
@pytest.mark.asyncio
async def test_asyncio_loop(harness) -> None:
    await _anyio_func(True, False)
    await _asyncio_func(False)

    # async with trio_asyncio.open_loop() as loop:  # noqa
    #     await _anyio_func(True, True)
    #     await _asyncio_func(True)
    #     await trio_asyncio.trio_as_aio(_trio_func)(True)


@skip_if_cant_import('trio_asyncio')
@pytest.mark.trio
async def test_trio_loop(harness) -> None:
    await _anyio_func(False, True)
    await _trio_func(False)

    async with trio_asyncio.open_loop() as loop:  # noqa
        await _anyio_func(True, True)
        await trio_asyncio.aio_as_trio(_asyncio_func)(True)
        await _trio_func(True)
