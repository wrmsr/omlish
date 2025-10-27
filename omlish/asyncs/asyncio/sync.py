# ruff: noqa: UP045
# @omlish-lite
import asyncio
import typing as ta

from ...sync import SyncBufferRelay
from ..sync import AsyncBufferRelay


T = ta.TypeVar('T')


##


@ta.final
class AsyncioBufferRelay(AsyncBufferRelay[T]):
    def __init__(
            self,
            *,
            event: ta.Optional[asyncio.Event] = None,
            loop: ta.Optional[ta.Any] = None,
    ) -> None:
        if event is None:
            event = asyncio.Event()
        self._event = event
        if loop is None:
            loop = asyncio.get_running_loop()
        self._loop = loop

        self._relay: SyncBufferRelay[T] = SyncBufferRelay(
            wake_fn=lambda: loop.call_soon_threadsafe(event.set),  # type: ignore[arg-type]
        )

    def push(self, *vs: T) -> None:
        self._relay.push(*vs)

    def swap(self) -> ta.Sequence[T]:
        return self._relay.swap()

    async def wait(self) -> None:
        await self._event.wait()
        self._event.clear()
