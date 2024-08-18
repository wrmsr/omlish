# -*- coding: utf-8 -*-


import asyncio

from asyncio import AbstractEventLoop, Queue
from contextlib import contextmanager
from functools import partial
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM,
    IPPROTO_UDP,
)
from typing import Callable, Iterator, Optional

from ._stack import AsyncExitStack, EnsureDone


@contextmanager
def udp_socket(host: str, port: int) -> Iterator[socket]:
    """Create, bind and cleanup a UDP socket.

    .. versionadded:: 0.4

    """

    s = socket(
        AF_INET,
        SOCK_DGRAM,
        IPPROTO_UDP,
    )
    try:
        s.bind((host, port))
        yield s
    finally:
        s.close()


def udp_reader(s: socket, iqueue: Queue, size: int) -> None:
    """Read one or more packets from an UDP socket."""

    data, peer = s.recvfrom(size)
    iqueue.put_nowait((peer, data))


async def udp_writer(s: socket, oqueue: Queue) -> None:
    """Forward packets to the UDP socket."""

    while True:
        peer, data = await oqueue.get()
        try:
            s.sendto(data, peer)
        finally:
            oqueue.task_done()


async def udp_server(
        host: str,
        port: int,
        service: Callable,
        loop: Optional[AbstractEventLoop] = None,
) -> None:
    """Simple UDP-based service.

    The only examples for UDP in asyncio documentation use protocols, the
    callback-based APIs and are a bit confusing (connection made?  connection
    lost?).

    This helper method tries to turn the low-level UDP socket support into a
    stream-based API.  You pass in a coroutine function to which a pair of
    queues will be passed.  From there, you can use async/await syntax to send
    and receive packets.

    :param host: Network interface on which to bind.
    :param port: Port number on which to bind.
    :service: coroutine that will perform logic.
    :param loop: Loop in which the service will run.

    The ``service`` coroutine should have the following signature:

    .. code-block:: python

       async def my_udp_service(*, iqueue, oqueue, loop, **kwds):
           pass

    The ``iqueue`` and ``oqueue`` parameters are ``asyncio.Queue`` objects that
    the coroutine can use to read from and write to, respectively.

    .. versionadded:: 0.4

    .. versionchanged:: 0.5 Added the ability to bind on a dynamically chosen
       port.

    """

    # Circular imports (yuk, fixme)!
    from . import reader

    loop = loop or asyncio.get_event_loop()

    async with AsyncExitStack() as stack:

        # Create & bind the socket.
        socket = await stack.enter_context(udp_socket(host, port))

        # Pair of queues through which packets will travel.
        iqueue = asyncio.Queue(loop=loop)  # type: Queue
        oqueue = asyncio.Queue(loop=loop)  # type: Queue

        # Forward packets from the queue to the socket.
        await stack.enter_context(EnsureDone(
            udp_writer(socket, oqueue=oqueue)
        ))

        try:
            # Forward packets from the socket to the queue.
            #
            # NOTE: if we want to be able to wait until all packets are sent
            #       using ``oqueue.join()``, we need to stop reading before we
            #       do that, which is why the ``reader()`` context manager is
            #       registered after (cleanup is LIFO).
            await stack.enter_context(reader(
                socket,
                partial(
                    udp_reader, socket,
                    iqueue=iqueue, size=2048,
                ),
            ))

            # Respond in the foreground until we're cancelled.
            return await service(iqueue=iqueue, oqueue=oqueue, loop=loop)
        finally:
            # Make sure to "flush" the output queue before leaving.
            await oqueue.join()
