import functools
import typing as ta

from .. import lang

if ta.TYPE_CHECKING:
    import trio_asyncio
else:
    trio_asyncio = lang.proxy_import('trio_asyncio')


def with_trio_asyncio_loop(fn):
    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        if trio_asyncio.current_loop.get() is None:
            async with trio_asyncio.open_loop():
                await fn(*args, **kwargs)
        else:
            await fn(*args, **kwargs)
    return inner
