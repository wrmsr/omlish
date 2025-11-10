import typing as ta

from .. import asyncs
from .sync import SyncStringInput


##


class AsyncStringInput(ta.Protocol):
    def __call__(self) -> ta.Awaitable[str]: ...


class ThreadAsyncStringInput:
    def __init__(self, child: SyncStringInput, runner: asyncs.AsyncThreadRunner) -> None:
        super().__init__()

        self._child = child
        self._runner = runner

    async def __call__(self) -> str:
        return await self._runner.run_in_thread(self._child)


class SyncAsyncStringInput:
    def __init__(self, child: SyncStringInput) -> None:
        super().__init__()

        self._child = child

    async def __call__(self) -> str:
        return self._child()
