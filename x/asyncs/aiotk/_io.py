# -*- coding: utf-8 -*-


import asyncio
from asyncio import AbstractEventLoop
from contextlib import contextmanager
from typing import Callable
from typing import Iterator
from typing import Optional


@contextmanager
def reader(
        fd,
        callback: Callable,
        loop: Optional[AbstractEventLoop] = None,
) -> Iterator[None]:
    """Register a low-level reader for a file descriptor.

    **Note**: the proactor event loop does not support readers.

    It's an easy mistake to forget a call to ``.remove_reader()`` and end up
    receiving extra I/O you were not interested in.  This context manager makes
    sure you never forget.

    :param fd: File descriptor to watch for read events.
    :param callback: Called when the file descriptor is ready to read from.
     See asyncio's documentation on ``loop.add_reader()`` for details.
    :param loop: Loop in which the watch will be registered.  Defaults to the
     current event loop.

    This context manager yields nothing.

    .. versionadded:: 0.4

    """

    loop = loop or asyncio.get_event_loop()

    loop.add_reader(fd, callback)
    try:
        yield
    finally:
        loop.remove_reader(fd)
