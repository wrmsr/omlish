"""
lookit:
 - https://github.com/davidbrochart/sqlite-anyio/blob/a3ba4c6ef0535b14a5a60071fcd6ed565a514963/sqlite_anyio/sqlite.py
 - https://github.com/rafalkrupinski/ratelimit-anyio/blob/2910a8a3d6fa54ed17ee6ba457686c9f7a4c4beb/src/ratelimit_anyio/__init__.py
 - https://github.com/nekitdev/async-extensions/tree/main/async_extensions
 - https://github.com/kinnay/anynet/tree/master/anynet
 - https://github.com/M-o-a-T/asyncscope
 - https://github.com/M-o-a-T/aevent
 - https://github.com/florimondmanca/aiometer
"""  # noqa
import typing as ta

import anyio


T = ta.TypeVar('T')


async def anyio_eof_to_empty(fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T | bytes:
    try:
        return await fn(*args, **kwargs)
    except anyio.EndOfStream:
        return b''
