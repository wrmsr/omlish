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


@flavors.mark_asyncio
async def _asyncio_func():
    await asyncio.sleep(0)
    assert sniffio.current_async_library() == 'asyncio'


@flavors.mark_trio
async def _trio_func():
    await trio.sleep(0)
    assert sniffio.current_async_library() == 'trio'


@flavors.mark_anyio
async def _anyio_func():
    await anyio.sleep(0)


##


@skip_if_cant_import('trio_asyncio')
@pytest.mark.asyncio
async def test_asyncio_loop(harness) -> None:
    await _asyncio_func()


@skip_if_cant_import('trio_asyncio')
@pytest.mark.trio
async def test_trio_loop(harness) -> None:
    await _trio_func()
    async with trio_asyncio.open_loop() as loop:  # noqa
        await trio_asyncio.aio_as_trio(_asyncio_func)()
    await _anyio_func()
