import typing as _ta

from .asyncio import AsyncioAsyncsBackend  # noqa
from .base import AsyncsBackend  # noqa
from .trio import TrioAsyncsBackend  # noqa
from .trio_asyncio import TrioAsyncioAsyncsBackend  # noqa


##


ASYNC_BACKENDS: _ta.Collection[type[AsyncsBackend]] = [
    AsyncioAsyncsBackend,
    TrioAsyncioAsyncsBackend,
    TrioAsyncsBackend,
]
