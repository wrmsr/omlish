# -*- coding: utf-8 -*-


import asyncio

from asyncio import AbstractEventLoop, Task
from typing import Any, Optional, Set


async def wait_until_cancelled(
        *,
        propagate: bool = True,
        loop: Optional[AbstractEventLoop] = None,
) -> None:
    """Wait until the calling task is canceled.

    **Note**: this function is a coroutine.

    When using a context manager to complete one or more background tasks, it's
    common to have the "main" task block until something cancels it (e.g. a
    SIGINT/CTRL-C handler).

    It's also convenient in tests that verify the behavior of cancellation to
    need to spawn a background task that waits forever.

    This leads to the not-so-idiomatic:

    .. code-block:: python

       await asyncio.Future()

    This of often wrapped in a helper function to make the call more readable.
    Instead of propagating multiple variants of this, it should be placed in a
    library that everybody can import.

    :param loop: Loop in which the coroutine will block.  Defaults to the
     current event loop.

    .. versionadded:: 0.3

    """

    loop = loop or asyncio.get_event_loop()

    if propagate:
        await asyncio.Future(loop=loop)
    else:
        try:
            await asyncio.Future(loop=loop)
        except asyncio.CancelledError:
            pass


async def cancel(task: Task, loop: Optional[AbstractEventLoop]=None) -> None:
    """Cancel a task and wait until it's done.

    **Note**: this function is a coroutine.

    Canceling a child task and returning without waiting for the child task to
    complete is a common cause of "event loop closed" ``RuntimeError``
    exceptions, especially during program shutdown.  Therefore, this becomes a
    common pattern:

    .. code-block:: python

        task.cancel()
        await asyncio.wait({task})

    However, if the parent task itself is also canceled, then the
    ``asyncio.wait()`` call will be interrupted and the child task will still
    not complete.  To solve this, we must also manage to trap the
    ``asyncio.CancelledError`` exception and call ``asyncio.wait({task})``
    again and properly re-raise the ``asyncio.CancelledError`` exception.  For
    example:


    .. code-block:: python

        task.cancel()
        try:
            await asyncio.wait({task})
        except asyncio.CancelledError:
            await asyncio.wait({task})
            raise

    This is not trivial and must be done so many times in a program that
    cancels tasks that it merits a replacement API for ``task.cancel()``.

    :param task: The ``asyncio.Task`` object to cancel.
    :param loop: The event loop to use for awaiting.  Defaults to the current
     event loop.

    .. versionadded:: 0.3

    """

    loop = loop or asyncio.get_event_loop()

    task.cancel()
    try:
        await asyncio.wait({task}, loop=loop)
    except asyncio.CancelledError:
        await asyncio.wait({task}, loop=loop)
        raise


async def cancel_all(
        tasks: Set[Task],
        loop: Optional[AbstractEventLoop] = None,
) -> None:
    """Cancel a set of tasks and wait until they're done.

    **Note**: this function is a coroutine.

    Canceling a set of child tasks and returning without waiting for the child
    task to complete is a common cause of "event loop closed" ``RuntimeError``
    exceptions, especially during shutdown of servers with one ore more task
    per connection.  Therefore, this becomes a common pattern:

    .. code-block:: python

        for task in tasks:
            task.cancel()
        await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    However, if the parent task itself is also canceled, then the
    ``asyncio.wait()`` call will be interrupted and one or more of the child
    tasks will still not complete.  To solve this, we must also manage to trap
    the ``asyncio.CancelledError`` exception and call ``asyncio.wait(tasks)``
    again and properly re-raise the ``asyncio.CancelledError`` exception.  For
    example:

    .. code-block:: python

        for task in tasks:
            task.cancel()
        try:
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        except asyncio.CancelledError:
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            raise

    This is not trivial and must be done so many server programs that cancels
    tasks that it merits a helper.

    :param tasks: The set of ``asyncio.Task`` objects to cancel.
    :param loop: The event loop to use for awaiting.  Defaults to the current
     event loop.

    .. versionadded:: 0.3

    """

    loop = loop or asyncio.get_event_loop()

    for task in tasks:
        task.cancel()
    try:
        await asyncio.wait(tasks, loop=loop)
    except asyncio.CancelledError:
        await asyncio.wait(tasks, loop=loop)
        raise


async def follow_through(
        task: Task,
        loop: Optional[AbstractEventLoop] = None,
) -> Any:
    """Wait for a task to complete (even if canceled while waiting).

    **Note**: this function is a coroutine.

    Not propagating cancellation to a child task and returning without waiting
    for the child task to complete is a common cause of "event loop closed"
    ``RuntimeError`` exceptions, especially during program shutdown.
    Therefore, this becomes a common pattern:

    .. code-block:: python

        try:
            await asyncio.wait({task})
        except asyncio.CancelledError:
            task.cancel()
            await asyncio.wait({task})
            raise
        return task.result()

    This is not trivial and must be done so many times in a program that spawns
    child tasks that it merits a helper method.

    :param task: The ``asyncio.Task`` object to see through to completion.
    :param loop: The event loop to use for awaiting.  Defaults to the current
     event loop.

    .. versionadded:: 0.3

    """

    loop = loop or asyncio.get_event_loop()

    try:
        await asyncio.wait({task}, loop=loop)
    except asyncio.CancelledError:
        await cancel(task, loop=loop)
        raise
    return task.result()
