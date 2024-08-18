# -*- coding: utf-8 -*-


import asyncio
import logging

from asyncio import AbstractEventLoop, Task
from typing import (
    Callable,
    Optional,
)
from typing import Set  # noqa: F401

from ._cancel import cancel, cancel_all
from ._stack import EnsureDone


class PoolClosed(Exception):
    pass


class TaskPool:
    """Collect background tasks.

    This is useful for server programs that wish to spawn one task per
    connection.  It removes the need to implement the redundant task management
    code required to close tasks as they complete and the need to implement
    graceful shutdown (with cancellation) to clean up when shutting down the
    server.

    .. versionadded:: 0.3

    """

    def __init__(self, loop: Optional[AbstractEventLoop]=None) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._lock = asyncio.Lock(loop=self._loop)
        self._cond = asyncio.Condition(self._lock, loop=self._loop)
        self._pool = set()  # type: Set
        self._task = None
        self._done = False
        self._idle = asyncio.Condition(self._lock, loop=self._loop)
        self._busy = asyncio.Condition(self._lock, loop=self._loop)

    async def spawn(self, fn: Callable, *args, **kwds) -> Task:
        """Add a new task to collect.

        The pool is designed to keep memory usage as low as possible by
        collecting tasks as soon as possible; it keeps no references to the
        task once it has completed.  If you want to get the task's result, you
        can keep a reference to the ``asyncio.Task`` object that is returned.

        :param fn: The coroutine function to invoke.
        :param args: Positional arguments to pass to the coroutine function.
        :param kwds: Keyword arguments to pass to the coroutine function.
        :return: An ``asyncio.Task`` object.

        """

        async with self._lock:

            # Ensure we don't spawn tasks after ``.close()`` is called.
            if self._done:
                raise PoolClosed()

            # Spawn the task.
            task = self._loop.create_task(fn(*args, **kwds))

            # Add the task.
            self._pool.add(task)

            # Signal the background task to update its wait list.
            self._cond.notify()

        return task

    async def wait_idle(self):
        """Block until all tasks have completed.

        This is useful to perform fan-in: spawn a set of tasks and then wait
        for all of them to complete.

        """

        async with self._lock:
            if self._done:
                raise PoolClosed()
            await self._idle.wait()

    async def wait_busy(self):
        """Block until the task is known to be waiting for tasks to complete.

        This is mostly useful for testing purposes (it avoids flaky behavior
        due to timing and makes the code paths more predictable).

        """
        async with self._lock:
            if self._done:
                raise PoolClosed()
            await self._busy.wait()

    async def __aenter__(self):
        """Perform the full startup sequence."""

        self.start()
        await self.wait_started()
        return self

    async def __aexit__(self, *args):
        """Perform the full shutdown sequence.


        This unblocks once all tasks in the pool have completed and that the
        collection task has completed.

        """

        self.close()
        await self.wait_closed()

    def start(self):
        """Start the collection task."""
        assert self._task is None
        self._task = self._loop.create_task(self._collect())

    async def wait_started(self):
        """Wait until the collection task has started."""
        assert self._task is not None
        async with self._lock:
            await self._idle.wait()

    def close(self):
        """Start the shutdown sequence."""

        assert self._task is not None

        # NO-OP: there's nothing we can do with a synchronous ``.close()``.

    async def wait_closed(self):
        """Wait until the shutdown sequence has completed.

        This unblocks once all tasks in the pool have completed and that the
        collection task has completed.

        """

        # Signal all tasks to start the shutdown sequence.
        async with self._lock:
            self._done = True
            self._cond.notify()

        # NOTE: don't hold the lock here else we'll prevent the shutdown from
        #       happening.
        if self._pool:
            await cancel_all(self._pool, loop=self._loop)
        await cancel(self._task)

    async def _collect(self):
        """Collect tasks that complete in the background."""

        # Main collection loop.
        while True:

            # Block until we have at least one task in the pool or until we are
            # told to shut down, which ever comes first.
            while not self._done and not self._pool:
                async with self._lock:
                    self._idle.notify()
                    await self._cond.wait()

            # Build a wait set containing all the tasks, plus a watch for
            # new tasks.
            async with self._lock:
                pending = set(task for task in self._pool)
                async with EnsureDone(self._cond.wait(),
                                      loop=self._loop) as watch:
                    pending.add(watch)

                    # NOTE: `self._cond.wait()` releases the lock until we're
                    #       notified, so we don't hold the lock while we block
                    #       on `asyncio.wait()`.
                    self._busy.notify()
                    done, pending = await asyncio.wait(
                        pending, return_when=asyncio.FIRST_COMPLETED,
                    )
                    for task in done:
                        if task is watch:
                            continue
                        self._pool.remove(task)

                        # Log exceptions for crashed tasks.
                        try:
                            task.result()
                        except asyncio.CancelledError:
                            pass
                        except Exception:
                            logging.exception('Task crashed!')
