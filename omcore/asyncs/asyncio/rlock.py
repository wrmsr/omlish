# MIT License
#
# Copyright (c) 2023 Joshua George Albert
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# https://github.com/Joshuaalbert/FairAsyncRLock/blob/7c3ed4e08892638dba262eaf0b1a7b1fad4b2608/fair_async_rlock/fair_async_rlock.py
import asyncio
import collections
import typing as ta


##


class AsyncioRLock:
    def __init__(self) -> None:
        super().__init__()

        self._owner: asyncio.Task | None = None
        self._count = 0
        self._owner_transfer = False
        self._queue: collections.deque[asyncio.Event] = collections.deque()

    def is_owner(self, task: asyncio.Task | None = None) -> bool:
        if task is None:
            task = asyncio.current_task()
        return self._owner == task

    def is_locked(self) -> bool:
        return self._owner is not None

    async def acquire(self) -> None:
        me = asyncio.current_task()

        # If the lock is reentrant, acquire it immediately
        if self.is_owner(task=me):
            self._count += 1
            return

        # If the lock is free (and ownership not in midst of transfer), acquire it immediately
        if not self._count and not self._owner_transfer:
            self._owner = me
            self._count = 1
            return

        # Create an event for this task, to notify when it's ready for acquire
        event = asyncio.Event()
        self._queue.append(event)

        # Wait for the lock to be free, then acquire
        try:
            await event.wait()
            self._owner_transfer = False
            self._owner = me
            self._count = 1

        except asyncio.CancelledError:
            try:  # if in queue, then cancelled before release
                self._queue.remove(event)

            except ValueError:  # otherwise, release happened, this was next, and we simulate passing on
                self._owner_transfer = False
                self._owner = me
                self._count = 1
                self._current_task_release()

            raise

    def _current_task_release(self) -> None:
        self._count -= 1
        if not self._count:
            self._owner = None

            if self._queue:
                # Wake up the next task in the queue
                event = self._queue.popleft()
                event.set()

                # Setting this here prevents another task getting lock until owner transfer.
                self._owner_transfer = True

    def release(self) -> None:
        me = asyncio.current_task()

        if self._owner is None:
            raise RuntimeError(f'Cannot release un-acquired lock. {me} tried to release.')

        if not self.is_owner(task=me):
            raise RuntimeError(f'Cannot release foreign lock. {me} tried to unlock {self._owner}.')

        self._current_task_release()

    async def __aenter__(self) -> ta.Self:
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.release()
