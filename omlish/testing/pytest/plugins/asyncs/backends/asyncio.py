import functools
import typing as ta

from ...... import lang
from .base import AsyncsBackend


if ta.TYPE_CHECKING:
    import asyncio
else:
    asyncio = lang.proxy_import('asyncio')


class AsyncioAsyncsBackend(AsyncsBackend):
    def wrap_runner(self, fn):
        @functools.wraps(fn)
        def wrapper(**kwargs):
            with asyncio.Runner(loop_factory=asyncio.new_event_loop) as runner:
                return runner.run(fn(**kwargs))

        return wrapper

    async def install_context(self, contextvars_ctx):
        pass