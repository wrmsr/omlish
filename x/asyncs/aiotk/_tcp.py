# -*- coding: utf-8 -*-


import asyncio

from asyncio import Future  # noqa: F401
from asyncio import StreamReader
from asyncio import StreamWriter
from asyncio import Task  # noqa: F401
from typing import Any  # noqa: F401
from typing import Callable
from typing import Optional
from typing import Set  # noqa: F401

from ._cancel import wait_until_cancelled
from ._typing import SocketServer


def _effective_bind_port(server: SocketServer) -> int:
    return server.sockets[0].getsockname()[1]


async def tcp_server(**kwds)-> None:
    """Run a TCP server in the foreground.

    **Note**: this function is a coroutine.

    This context manager provides the following features over direct use of
    ``asyncio.create_server()``:

    - runs in the foreground, blocking the calling task
    - automatically closes the server object with graceful shutdown.

    There are two main difference with the related :py:class:`~TCPServer`:

    - based on ``asyncio.create_server()`` for compatibility with libraries
      that are based on protocols (asyncio's callback API)
    - runs in the foreground

    .. versionadded:: 0.3

    """

    loop = kwds.pop('loop', None) or asyncio.get_event_loop()

    server = await loop.create_server(**kwds)
    try:
        await wait_until_cancelled(loop=loop)
    finally:
        server.close()
        await server.wait_closed()


class TCPServer(object):
    """Asynchronous context manager to accept TCP connections.

    This context manager provides the following features over direct use of
    ``asyncio.start_server()``:

    - connection handlers are coroutines
    - prevent leaking connections when the writer is not properly closed by the
      connection handler
    - automatically cancel all tasks that handle connections when it's time to
      shut down
    - wait until all connections are closed before shutting down the server
      application (includes handling of a rare race condition)

    :param host: Network interface on which to listen for incoming connections.

    :param port: Port number on which to listen for incoming connections.  You
     can pass a value of zero to ask the system to pick an available port for
     you.  After ``wait_started()``, the ``port`` property will contain the
     port number on which the server is listening.
    :param callback: Coroutine function that will be used to spawn a task for
     each established connection.  This coroutine must accept two positional
     arguments: ``(reader, writer)`` which allow interaction with the peer.
    :param loop: Event loop in which to run the server's asynchronous tasks.
     When ``None``, the current default event loop will be used.

    .. versionadded:: 0.2

    """

    def __init__(
            self,
            host: str,
            port: int,
            callback: Callable,
            loop=None,
    ) -> None:
        self._callback = callback
        self._host = host
        self._port = port
        self._loop = loop or asyncio.get_event_loop()
        self._sessions = set()  # type: Set[Task]
        self._boot = None  # type: Optional[Task]
        self._server = None  # type: Optional[SocketServer]

    @property
    def host(self) -> str:
        """Network interface on which the server listens for connections.

        See:

        - :py:data:`aiotk.TCPServer.port`
        """
        return self._host

    @property
    def port(self) -> int:
        """Port number on which the server listens for connections.

        See:

        - :py:data:`aiotk.TCPServer.host`

        .. versionchanged:: 0.4.1

           When asking the system to choose the available port, this property
           now returns the actual port number (rather than zero).

        """
        return self._port

    # NOTE: cannot declare type for return value here because the class
    #       definition is not completed...
    async def __aenter__(self):
        self.start()
        await self.wait_started()
        return self

    async def __aexit__(self, *args) -> Optional[bool]:
        self.close()
        await self.wait_closed()
        # NOTE: `mypy` will not allow `return` without an expression even when
        #       it accepts `None`...
        return None

    def start(self) -> None:
        """Start accepting connections.

        Only use this method if you are not using the server as an asynchronous
        context manager.

        See:

        - :py:meth:`aiotk.TCPServer.wait_started`
        - :py:meth:`aiotk.TCPServer.close`
        """
        if self._boot:
            raise Exception('Already running.')
        self._boot = self._loop.create_task(asyncio.start_server(
            self._client_connected, host=self._host, port=self._port,
        ))

    # NOTE: start is synchronous, so we can't await in there.
    async def wait_started(self) -> None:
        """Wait until the server is ready to accept connections.

        See:

        - :py:meth:`aiotk.TCPServer.start`
        - :py:meth:`aiotk.TCPServer.close`
        """
        if not self._boot:
            raise Exception('Not started.')
        if self._server is None:
            self._server = await self._boot
            assert self._server is not None
            self._port = _effective_bind_port(self._server)

    # NOTE: cancel pending sessions immediately.
    #
    # TODO: make cancelling session optionnal (graceful shutdown).
    def close(self) -> None:
        """Stop accepting connections.

        .. note::

           Since connections may still be pending in the kernel's TCP stack at
           the time where you call this, it's possible that new connections
           seem to get established after you signal your intent to stop
           accepting connections.

        See:

        - :py:meth:`aiotk.TCPServer.wait_started`
        - :py:meth:`aiotk.TCPServer.wait_closed`

        """
        if self._boot and not self._boot.done():
            raise Exception('Starting.')
        if not self._server:
            return
        self._server.close()
        for session in self._sessions:
            session.cancel()

    # NOTES:
    # - caller can retry if they hit the timeout;
    # - not clear if we can still accept connections until
    #   ```self._server.wait_closed()` completes, so we cancel again after it
    #   does.
    async def wait_closed(self, timeout=None) -> None:
        """Wait until all connections are closed.

        See:

        - :py:meth:`aiotk.TCPServer.wait_started`
        - :py:meth:`aiotk.TCPServer.wait_closed`
        """

        if not self._server:
            return
        await self._server.wait_closed()
        for session in self._sessions:
            session.cancel()
        pending = {t for t in self._sessions}  # type: Set[Future[Any]]
        if pending:
            _, pending = await asyncio.wait(
                pending,
                return_when=asyncio.ALL_COMPLETED,
                timeout=timeout,
            )
        if pending:
            raise asyncio.TimeoutError()
        assert not self._sessions

    # NOTE: not closing writer here leaks connection.
    async def _client_wrapper(
            self,
            reader: StreamReader,
            writer: StreamWriter,
    ) -> None:
        try:
            return await self._callback(
                reader=reader, writer=writer,
            )
        except asyncio.CancelledError:
            pass
        finally:
            writer.close()

    # NOTE: exception here leaks connection.
    def _client_connected(
            self,
            reader: StreamReader,
            writer: StreamWriter,
    ):
        s = self._loop.create_task(
            self._client_wrapper(reader, writer)
        )
        s.add_done_callback(self._sessions.remove)
        self._sessions.add(s)
