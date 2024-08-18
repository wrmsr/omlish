# -*- coding: utf-8 -*-


import asyncio
import os
import contextlib
import signal

from asyncio import AbstractEventLoop  # noqa: F401
from asyncio import Future
from asyncio import StreamReader
from asyncio import StreamWriter
from asyncio import Task  # noqa: F401
from typing import Any  # noqa: F401
from typing import Callable
from typing import Iterator
from typing import Optional
from typing import Set  # noqa: F401
from typing import Union  # noqa: F401

from ._typing import Server  # noqa: F401


@contextlib.contextmanager
def handle_ctrlc(f: Future, loop=None) -> Iterator[None]:
    """Context manager that schedules a callback when SIGINT is received.

    :param f: future to fulfill when SIGINT is received.  Will only be set
     once even if SIGINT is received multiple times.
    :param loop: event loop (defaults to global event loop).

    .. versionadded:: 0.2

    """

    loop = loop or asyncio.get_event_loop()

    def handler():
        if not f.done():
            f.set_result(None)

    loop.add_signal_handler(signal.SIGINT, handler)
    try:
        yield
    finally:
        loop.remove_signal_handler(signal.SIGINT)


class UnixSocketServer(object):
    """Asynchronous context manager to accept UNIX connections.

    This context manager provides the following features over direct use of
    ``asyncio.start_unix_server()``:

    - connection handlers are coroutines
    - prevent leaking connections when the writer is not properly closed by the
      connection handler
    - automatically cancel all tasks that handle connections when it's time to
      shut down
    - wait until all connections are closed before shutting down the server
      application (includes handling of a rare race condition)
    - automatically unlink the UNIX socket when shutting down (assuming the
      process does not crash)

    :param path: Path to the UNIX socket on which to listen for incoming
     connections.
    :param callback: Coroutine function that will be used to spawn a task for
     each established connection.  This coroutine must accept two positional
     arguments: ``(reader, writer)`` which allow interaction with the peer.
    :param loop: Event loop in which to run the server's asynchronous tasks.
     When ``None``, the current default event loop will be used.

    .. versionadded:: 0.1

    """

    def __init__(
            self,
            path: str,
            callback: Callable,
            loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        self._callback = callback
        self._path = path
        self._loop = loop or asyncio.get_event_loop()
        self._sessions = set()  # type: Set[Task]
        self._boot = None  # type: Optional[Task]
        self._server = None  # type: Optional[Server]

    @property
    def path(self) -> str:
        """UNIX socket on which the server listens for incoming connections."""
        return self._path

    # NOTE: cannot declare type for return value here because the class
    #       definition is not completed...
    async def __aenter__(self):
        self.start()
        await self.wait_started()
        return self

    async def __aexit__(self, *args) -> None:
        self.close()
        await self.wait_closed()

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
        start_unix_server = asyncio.start_unix_server  # type: ignore
        self._boot = self._loop.create_task(start_unix_server(
            self._client_connected, path=self._path, loop=self._loop,
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

    # NOTE: cancel pending sessions immediately.
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
        # NOTE: there is a natural race here and we could not manage to
        #       reliably reach this branch while the boot task had not yet
        #       completed.
        if self._boot and not self._boot.done():
            raise Exception('Starting.')  # pragma: no cover
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
    async def wait_closed(self, timeout: Optional[float]=None) -> None:
        """Wait until all connections are closed.

        See:

        - :py:meth:`aiotk.TCPServer.wait_started`
        - :py:meth:`aiotk.TCPServer.wait_closed`
        """
        # NOTE: there is a natural race here and we could not manage to
        #       reliably reach this branch while the boot task had not yet
        #       completed.
        if self._boot and not self._boot.done():
            raise Exception('Starting.')  # pragma: no cover
        if not self._server:
            return
        await self._server.wait_closed()
        for session in self._sessions:
            session.cancel()
        # NOTE: `mypy` does not recognize `Set[Task[Any]]` as a subtype of
        #       `Set[Future[Any]]`.  The only way to resolve this is to create
        #       a copy...
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
        if os.path.exists(self._path):
            os.unlink(self._path)

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
    ) -> None:
        s = self._loop.create_task(
            self._client_wrapper(reader, writer)
        )
        s.add_done_callback(self._sessions.remove)
        self._sessions.add(s)
