# -*- coding: utf-8 -*-


import asyncio
import sys

from asyncio import AbstractEventLoop
from typing import Awaitable

from ._cancel import (
    cancel,
    cancel_all,
    follow_through,
    wait_until_cancelled,
)
from ._io import reader
from ._mempipe import mempipe
from ._monkey import monkey_patch
from ._pool import PoolClosed, TaskPool
from ._sched import PeriodicTask
from ._stack import AsyncExitStack, EnsureDone
from ._tcp import TCPServer, tcp_server
from ._testing import mock_subprocess
from ._udp import udp_server, udp_socket

if sys.platform != 'win32':  # pragma: no cover
    from ._posix import (
        handle_ctrlc,
        UnixSocketServer,
    )


def run_until_complete(coro: Awaitable, loop: AbstractEventLoop=None):
    """Run a task through to completion.

    The ``.run_until_complete()`` method on asyncio event loop objects does not
    finish tasks when it receives a SIGINT/CTRL-C.  The method simply raises a
    ``KeyboardInterrupt`` exception and this usually results in warnings about
    unfinished tasks plus some "event loop closed" ``RuntimeError`` exceptions
    in pending tasks.

    This is a really annoying default behavior and this function aims at
    replacing that behavior with something that ensures the task actually runs
    through to completion.  When the ``KeyboardInterrupt`` exception is caught,
    the task is canceled and resumed to give it a chance to clean up properly.

    .. versionadded:: 0.4
    .. versionchanged:: 0.5 Can now be called with a ``asyncio.Task`` argument.

    """

    loop = loop or asyncio.get_event_loop()
    if isinstance(coro, asyncio.Task):
        task = coro
    else:
        task = loop.create_task(coro)
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            return None
    return task.result()


__all__ = [
    'AsyncExitStack',
    'cancel',
    'cancel_all',
    'EnsureDone',
    'follow_through',
    'handle_ctrlc',
    'mempipe',
    'mock_subprocess',
    'monkey_patch',
    'PeriodicTask',
    'PoolClosed',
    'reader',
    'run_until_complete',
    'TaskPool',
    'TCPServer',
    'tcp_server',
    'udp_server',
    'udp_socket',
    'UnixSocketServer',
    'wait_until_cancelled',
]
