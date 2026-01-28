# ruff: noqa: UP045
import math
import queue
import typing as ta

import anyio
import anyio.streams.memory

from ..queues import AsyncliteQueue
from ..queues import AsyncliteQueues
from .base import AnyioAsyncliteApi
from .base import AnyioAsyncliteObject


T = ta.TypeVar('T')


##


class AnyioAsyncliteQueue(AsyncliteQueue[T], AnyioAsyncliteObject):
    def __init__(
            self,
            send: anyio.streams.memory.MemoryObjectSendStream[T],
            recv: anyio.streams.memory.MemoryObjectReceiveStream[T],
            maxsize: int,
    ) -> None:
        super().__init__()

        self._send = send
        self._recv = recv
        self._maxsize = maxsize

    async def aclose(self) -> None:
        await self._send.aclose()
        await self._recv.aclose()

    def qsize(self) -> int:
        return self._recv.statistics().current_buffer_used

    def empty(self) -> bool:
        return self.qsize() == 0

    def full(self) -> bool:
        if self._maxsize <= 0:
            return False

        return self.qsize() >= self._maxsize

    async def put(self, item: T, *, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None:
            with anyio.fail_after(timeout):
                await self._send.send(item)

        else:
            await self._send.send(item)

    def put_nowait(self, item: T) -> None:
        try:
            self._send.send_nowait(item)

        except anyio.WouldBlock as e:
            raise queue.Full from e

    async def get(self, *, timeout: ta.Optional[float] = None) -> T:
        if timeout is not None:
            with anyio.fail_after(timeout):
                return await self._recv.receive()

        else:
            return await self._recv.receive()

    def get_nowait(self) -> T:
        try:
            return self._recv.receive_nowait()

        except anyio.WouldBlock as e:
            raise queue.Empty from e


class AnyioAsyncliteQueues(AsyncliteQueues, AnyioAsyncliteApi):
    def make_queue(self, maxsize: int = 0) -> AsyncliteQueue:
        # anyio interprets 0 as "no buffer" (synchronous handoff), but stdlib queue uses 0 for unbounded. Convert 0 to
        # math.inf for anyio to get unbounded behavior.
        anyio_maxsize = math.inf if maxsize == 0 else maxsize
        send, recv = anyio.create_memory_object_stream(anyio_maxsize)
        return AnyioAsyncliteQueue(send, recv, maxsize)
