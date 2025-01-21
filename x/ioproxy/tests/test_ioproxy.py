import asyncio
import contextlib
import functools
import typing as ta

import pytest

from ..proxier import AsyncIoProxier
from ..proxy import AsyncIoProxyTarget


##


class AsyncioAsyncIoProxier(AsyncIoProxier):
    def __init__(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        super().__init__()

        self._loop = loop

    def get_loop(self) -> asyncio.AbstractEventLoop:
        if (l := self._loop) is not None:
            return l
        return asyncio.get_running_loop()

    def target_obj(self, obj: ta.Any) -> AsyncIoProxyTarget:
        loop = self.get_loop()
        runner = functools.partial(loop.run_in_executor, None)
        return AsyncIoProxyTarget(obj, runner)


ASYNCIO_ASYNC_IO_PROXIER = AsyncioAsyncIoProxier()

asyncio_io_proxy = ASYNCIO_ASYNC_IO_PROXIER.proxy_obj


##


@contextlib.asynccontextmanager
async def async_open(*args, **kwargs):
    loop = asyncio.get_running_loop()
    f = await loop.run_in_executor(None, functools.partial(open, *args, **kwargs))
    af = asyncio_io_proxy(f)
    async with af:
        yield af


##


@pytest.mark.asyncs('asyncio')
async def test_io_proxy():
    with open('pyproject.toml') as f:
        p = asyncio_io_proxy(f)
        print(p.fileno())
        print(await p.read())

    async with async_open('pyproject.toml') as af:
        print(af.fileno())
        print(await af.read())
