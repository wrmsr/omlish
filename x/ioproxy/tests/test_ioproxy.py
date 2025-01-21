import asyncio
import functools
import typing as ta

import pytest

from ..proxier import AsyncIoProxier
from ..proxy import AsyncIoProxyRunner
from ..typing import TypingBinaryIOAsyncIoProxy
from ..typing import TypingIOAsyncIoProxy
from ..typing import TypingTextIOAsyncIoProxy


if not ta.TYPE_CHECKING:
    reveal_type = lambda _: None


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


def asyncio_open(
        file: ta.Any,
        mode: str = 'r',
        *args: ta.Any,
        **kwargs: ta.Any,
) -> ta.Awaitable[TypingIOAsyncIoProxy[ta.Any]]:
    return _asyncio_open(file, mode, *args, **kwargs)


def asyncio_open_binary(
        file: ta.Any,
        mode: str = 'r',
        *args: ta.Any,
        **kwargs: ta.Any,
) -> ta.Awaitable[TypingBinaryIOAsyncIoProxy]:
    return _asyncio_open(file, mode, *args, **kwargs)


def asyncio_open_text(
        file: ta.Any,
        mode: str = 'rb',
        *args: ta.Any,
        **kwargs: ta.Any,
) -> ta.Awaitable[TypingTextIOAsyncIoProxy]:
    return _asyncio_open(file, mode, *args, **kwargs)


##


@pytest.mark.asyncs('asyncio')
async def test_io_proxy():
    # def barf() -> ta.Awaitable[int]:
    #     async def f():
    #         return 1
    #
    #     return f()
    #
    # b = barf()
    # reveal_type(b)

    async def poke(af):
        print(af.fileno())
        print(len(await af.read()))

    with open('pyproject.toml') as sf:  # noqa
        reveal_type(sf)
        # af1 = asyncio_io_proxy(sf)
        af1 = ASYNCIO_ASYNC_IO_PROXIER.proxy_obj(sf)
        reveal_type(af1)
        await poke(af1)

    async with await asyncio_io_proxy(open)('pyproject.toml') as af2:  # noqa
        reveal_type(af2)
        await poke(af2)

    async with await asyncio_open_text('pyproject.toml') as af3:
        reveal_type(af3)
        await poke(af3)

    af4 = await asyncio_open_text('pyproject.toml')
    try:
        reveal_type(af4)
        await poke(af4)
    finally:
        await af4.close()
