import asyncio
import typing as ta

from .types import WaitableEvent
from .types import WaitableEventWrapper


class WorkerContext:
    event_class: type[WaitableEvent] = WaitableEventWrapper

    def __init__(self, max_requests: ta.Optional[int]) -> None:
        super().__init__()
        self.max_requests = max_requests
        self.requests = 0
        self.terminate = self.event_class()
        self.terminated = self.event_class()

    async def mark_request(self) -> None:
        if self.max_requests is None:
            return

        self.requests += 1
        if self.requests > self.max_requests:
            await self.terminate.set()

    @staticmethod
    async def sleep(wait: ta.Union[float, int]) -> None:
        return await asyncio.sleep(wait)

    @staticmethod
    def time() -> float:
        return asyncio.get_event_loop().time()


class ShutdownError(Exception):
    pass
