import typing as ta

import anyio


T = ta.TypeVar('T')


async def anyio_eof_to_empty(fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T | bytes:
    try:
        return await fn(*args, **kwargs)
    except anyio.EndOfStream:
        return b''
