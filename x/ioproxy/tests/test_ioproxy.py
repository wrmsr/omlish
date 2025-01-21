import asyncio
import functools
import typing as ta

import pytest

from ..proxier import AsyncIoProxier
from ..proxy import AsyncIoProxyRunner
from ..typing import TypingBinaryIOAsyncIoProxy
from ..typing import TypingIOAsyncIoProxy
from ..typing import TypingTextIOAsyncIoProxy


##


class AsyncioAsyncIoProxier(AsyncIoProxier):
    def __init__(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        super().__init__()

        self._loop = loop

    def get_runner(self) -> AsyncIoProxyRunner:
        if (loop := self._loop) is not None:
            return functools.partial(loop.run_in_executor, None)
        else:
            def run(fn, *args, **kwargs):
                return asyncio.get_running_loop().run_in_executor(None, fn, *args, **kwargs)
            return run


ASYNCIO_ASYNC_IO_PROXIER = AsyncioAsyncIoProxier()

asyncio_io_proxy = ASYNCIO_ASYNC_IO_PROXIER.proxy


##


_asyncio_open = ASYNCIO_ASYNC_IO_PROXIER.proxy_fn(open)


async def asyncio_open(file, mode='r', *args, **kwargs) -> TypingIOAsyncIoProxy[ta.Any]:
    return await _asyncio_open(file, mode, *args, **kwargs)


async def asyncio_open_binary(file, mode='r', *args, **kwargs) -> TypingBinaryIOAsyncIoProxy:
    return await _asyncio_open(file, mode, *args, **kwargs)


async def asyncio_open_text(file, mode='rb', *args, **kwargs) -> TypingTextIOAsyncIoProxy:
    return await _asyncio_open(file, mode, *args, **kwargs)


##


@pytest.mark.asyncs('asyncio')
async def test_io_proxy():
    with open('pyproject.toml') as sf:  # noqa
        af1 = asyncio_io_proxy(sf)
        print(af1.fileno())
        print(await af1.read())

    async with await asyncio_io_proxy(open)('pyproject.toml') as af2:  # noqa
        print(af2.fileno())
        print(await af2.read())

    async with await asyncio_open('pyproject.toml') as af3:
        print(af3.fileno())
        print(await af3.read())
