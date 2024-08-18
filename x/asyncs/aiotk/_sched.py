# -*- coding: utf-8 -*-


import asyncio
import logging

from aiotk import cancel
from asyncio import AbstractEventLoop
from asyncio import Task  # noqa: F401
from typing import Callable, Optional


class PeriodicTask:
    """Periodically run a coroutine in the background.

    .. code-block:: python

       async def my_task():
           pass

       async with PeriodicTask(my_task, 30.0):
           # do something for a long time.

    .. versionadded:: 0.5

    """

    def __init__(
            self,
            func: Callable,
            interval: float,
            loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._func = func
        self._ival = interval
        self._task = None  # type: Optional[Task]

    # NOTE: cannot declare type for return value here because the class
    #       definition is not completed...
    async def __aenter__(self):
        """Schedule the background task."""
        assert self._task is None
        self._task = self._loop.create_task(self._run())
        return self

    async def __aexit__(self, *args) -> None:
        """Stop the background task and wait for it to complete."""
        assert self._task
        await cancel(self._task)
        self._task = None

    async def _run(self) -> None:
        """Periodically run the task and wait until the schedule."""
        while True:
            try:
                await self._func()
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.exception('Executing periodic task.')
            await asyncio.sleep(self._ival)
