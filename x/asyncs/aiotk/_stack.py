# -*- coding: utf-8 -*-


import asyncio
import sys

from aiotk import cancel, follow_through
from asyncio import Task
from typing import (
    Any,
    Awaitable,
    ContextManager,
    Optional,
    overload,
)

from typing_extensions import AsyncContextManager


class EnsureDone:
    """Ensure a background task completes before leaving a code block.

    This is mostly useful for spawning multiple tasks in the background using
    :py:class:`~AsyncExitStack`, but it can also be used directly for single
    tasks.

    .. source-code: python

    .. versionadded:: 0.3

    """

    # NOTE: the type of `coro` should be `typing.Coroutine` to reject futures,
    #       tasks and other awaitables (`loop.create_task()` does not accept
    #       them), but there is a bug in `mypy` which causes the return type of
    #       coroutine functions to be reported as `typing.Awaitable`.
    def __init__(self, coro: Awaitable, cancel=True, loop=None) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._coro = coro
        self._task = None  # type: Optional[Task]
        self._cancel = cancel

    async def __aenter__(self) -> Task:
        """Spawn the background task."""

        self._task = self._loop.create_task(self._coro)
        return self._task

    async def __aexit__(self, *args) -> None:
        """Wait until the task completes.

        If ``cancel=True`` was passed to the constructor, the task is cancelled
        before being awaited.

        """
        assert self._task
        if self._cancel:
            await cancel(self._task, loop=self._loop)
        else:
            await follow_through(self._task, loop=self._loop)


class AsyncExitStack(object):
    """Rollback stack for asynchronous context managers.

    This context manager provides the following features over direct use of
    ``contextlib.ExitStack``:

    - supports asynchronous context managers (in addition to regular context
      managers).

    .. versionadded:: 0.2

    """

    def __init__(self):
        self._stack = []

    # NOTE: cannot declare type for return value here because the class
    #       definition is not completed...
    async def __aenter__(self):
        """No-op."""
        assert self._stack == []
        return self

    async def __aexit__(self, etype, exc, tb) -> Optional[bool]:
        """Pop all context managers from the rollback stack.

        :param context: context manager or asynchronous context manager.
        :returns: True if one of the context managers in the stack suppressed
         the exception by returning a ``True`` value from its ``__exit__`` or
         ``__aexit__`` method.
        :exception: If any context manager in the stack raises an exception
         from its ``__exit__`` or ``__aexit__`` method, this exception will
         replace the original exception for context managers lower in the stack
         and will eventually be propagated to the caller.

        """
        changed = False
        for context in reversed(self._stack):
            suppress = False
            try:
                if hasattr(context, '__aexit__'):
                    suppress = await context.__aexit__(etype, exc, tb)
                if hasattr(context, '__exit__'):
                    suppress = context.__exit__(etype, exc, tb)
                if suppress:
                    etype, exc, tb = (None, None, None)
                    changed = True
            except Exception:
                etype, exc, tb = sys.exc_info()
                changed = True
        if changed:
            if (etype, exc, tb) == (None, None, None):
                return True
            raise exc
        return None

    @overload
    async def enter_context(self, context: ContextManager) -> Any:
        ...  # pragma: no cover

    @overload  # noqa: F811
    async def enter_context(self, context: AsyncContextManager) -> Any:
        ...  # pragma: no cover

    async def enter_context(self, context):  # noqa: F811
        """Push an (asynchronous) context manager onto the rollback stack.

        :param context: context manager or asynchronous context manager.
        :return: The return value of the context manager's ``__enter__`` or
         ``__aenter__`` method.

        """
        if hasattr(context, '__aenter__'):
            r = await context.__aenter__()
        else:
            r = context.__enter__()
        self._stack.append(context)
        return r
