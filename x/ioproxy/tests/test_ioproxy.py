import asyncio
import contextlib
import functools

import pytest

from ..proxier import AsyncIoProxier
from ..proxy import AsyncIoProxyRunner


##


class AsyncioAsyncIoProxier(AsyncIoProxier):
    def __init__(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        super().__init__()

        self._loop = loop

    def get_loop(self) -> asyncio.AbstractEventLoop:
        if (l := self._loop) is not None:
            return l
        return asyncio.get_running_loop()

    def get_runner(self) -> AsyncIoProxyRunner:
        loop = self.get_loop()
        runner = functools.partial(loop.run_in_executor, None)
        return runner


ASYNCIO_ASYNC_IO_PROXIER = AsyncioAsyncIoProxier()

asyncio_io_proxy = ASYNCIO_ASYNC_IO_PROXIER.proxy_obj


##


@contextlib.asynccontextmanager
async def async_open(*args, **kwargs):
    proxier = ASYNCIO_ASYNC_IO_PROXIER
    async with (af := await proxier.proxy_fn(open, wrap_result=True)(*args, **kwargs)):
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
