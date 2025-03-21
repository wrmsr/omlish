import functools
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import asyncio

    import sniffio
    import trio_asyncio

else:
    asyncio = lang.proxy_import('asyncio')

    sniffio = lang.proxy_import('sniffio')
    trio_asyncio = lang.proxy_import('trio_asyncio')


##


def check_trio_asyncio() -> None:
    if trio_asyncio.current_loop.get() is None:
        raise RuntimeError('trio_asyncio loop not running')


def with_trio_asyncio_loop(*, wait=False, strict=False):
    def outer(fn):
        @functools.wraps(fn)
        async def inner(*args, **kwargs):
            if trio_asyncio.current_loop.get() is not None:
                await fn(*args, **kwargs)
                return

            if sniffio.current_async_library() != 'trio':
                if strict:
                    raise RuntimeError('trio loop not running')
                await fn(*args, **kwargs)
                return

            loop: asyncio.BaseEventLoop
            async with trio_asyncio.open_loop() as loop:
                try:
                    await fn(*args, **kwargs)
                finally:
                    if wait:
                        # FIXME: lol
                        while asyncio.all_tasks(loop):
                            await asyncio.sleep(.1)

        return inner

    return outer
