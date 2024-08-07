"""
TODO:
 - these are just anyio.TaskGroup lol
"""
import anyio.abc

from omlish import lang

from .types import Context


class ContextImpl(Context, lang.Final):
    def __init__(self) -> None:
        super().__init__()

        self._done = anyio.Event()

    async def done(self) -> None:
        await self._done.wait()

    def err(self) -> Exception | None:
        raise NotImplementedError
