import functools
import typing as ta

from .. import lang

if ta.TYPE_CHECKING:
    import sniffio
    import trio_asyncio
else:
    sniffio = lang.proxy_import('sniffio')
    trio_asyncio = lang.proxy_import('trio_asyncio')


def check_trio_asyncio() -> None:
    if trio_asyncio.current_loop.get() is None:
        raise RuntimeError('trio_asyncio loop not running')


def with_trio_asyncio_loop(fn):
    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        if trio_asyncio.current_loop.get() is None:
            if sniffio.current_async_library() != 'trio':
                raise RuntimeError('trio loop not running')
            async with trio_asyncio.open_loop():
                await fn(*args, **kwargs)
        else:
            await fn(*args, **kwargs)
    return inner
