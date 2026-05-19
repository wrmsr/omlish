import anyio

from .types import WaitableEvent


##


class WaitableEventWrapper:
    def __init__(self) -> None:
        super().__init__()

        self._event = anyio.Event()

    async def clear(self) -> None:
        self._event = anyio.Event()

    async def wait(self) -> None:
        await self._event.wait()

    async def set(self) -> None:
        self._event.set()

    def is_set(self) -> bool:
        return self._event.is_set()


class WorkerContext:
    event_class: type[WaitableEvent] = WaitableEventWrapper

    def __init__(self, max_requests: int | None) -> None:
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
    async def sleep(wait: float) -> None:
        return await anyio.sleep(wait)

    @staticmethod
    def time() -> float:
        return anyio.current_time()


class ShutdownError(Exception):
    pass
