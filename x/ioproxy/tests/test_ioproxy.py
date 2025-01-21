import asyncio
import functools

import pytest

from ..proxier import AsyncIoProxier
from ..proxy import AsyncIoProxyRunner


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

asyncio_io_proxy = ASYNCIO_ASYNC_IO_PROXIER.proxy_obj


##


asyncio_open = ASYNCIO_ASYNC_IO_PROXIER.proxy_fn(open, wrap_result=True)


##


@pytest.mark.asyncs('asyncio')
async def test_io_proxy():
    with open('pyproject.toml') as f:  # noqa
        p = asyncio_io_proxy(f)
        print(p.fileno())
        print(await p.read())

    async with await asyncio_open('pyproject.toml') as af:
        print(af.fileno())
        print(await af.read())
