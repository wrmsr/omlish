#!/usr/bin/env python3
"""
asyncio Unix-socket stdio relay.

Roughly equivalent socat incantation:

    socat - UNIX-CONNECT:/path/to/socket

or, if you want to be very explicit about stdio:

    socat STDIO UNIX-CONNECT:/path/to/socket
"""
import argparse
import asyncio
import os
import signal
import sys
import types
import typing as ta


Timeout: ta.TypeAlias = float | None


##


def parse_timeout(s: str) -> Timeout:
    if s.lower() in {'none', 'off', 'disabled', 'disable'}:
        return None

    v = float(s)
    if v < 0:
        raise argparse.ArgumentTypeError("timeout must be >= 0, or 'none'")
    return v


class UnixSocketRelay:
    def __init__(
            self,
            input_fd: int,
            output_fd: int,
            socket_path: str,
            *,
            buffer_size: int = 64 * 1024,
            connect_timeout: Timeout = 10.0,
            read_timeout: Timeout = None,
            write_timeout: Timeout = 30.0,
            shutdown_timeout: Timeout = 5.0,
    ) -> None:
        self._input_fd = input_fd
        self._output_fd = output_fd
        self._socket_path = socket_path

        self._buffer_size = buffer_size
        self._connect_timeout = connect_timeout
        self._read_timeout = read_timeout
        self._write_timeout = write_timeout
        self._shutdown_timeout = shutdown_timeout

        self._closing: asyncio.Event | None = None
        self._tasks: set[asyncio.Task[ta.Any]] = set()

        self._input_transport: asyncio.BaseTransport | None = None
        self._output_transport: asyncio.BaseTransport | None = None
        self._socket_writer: asyncio.StreamWriter | None = None

        self._started = False

    @property
    def input_fd(self) -> int:
        return self._input_fd

    @property
    def output_fd(self) -> int:
        return self._output_fd

    @property
    def socket_path(self) -> str:
        return self._socket_path

    #

    async def __aenter__(self) -> ta.Self:
        await self.start()
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: types.TracebackType | None,
    ) -> None:
        await self.aclose()

    #

    async def run(self) -> None:
        async with self:
            await self.wait()

    async def start(self) -> None:
        if self._started:
            raise RuntimeError('relay already started')

        self._started = True
        self._closing = asyncio.Event()

        socket_reader, socket_writer = await self._with_timeout(
            asyncio.open_unix_connection(self._socket_path),
            self._connect_timeout,
            'timed out connecting to unix socket',
        )
        self._socket_writer = socket_writer

        fd_reader = await self._open_fd_reader(self._input_fd)
        fd_writer = await self._open_fd_writer(self._output_fd)

        self._tasks = {
            asyncio.create_task(
                self._copy_fd_to_socket(fd_reader, socket_writer),
                name='unix-relay-fd-to-socket',
            ),
            asyncio.create_task(
                self._copy_socket_to_fd(socket_reader, fd_writer),
                name='unix-relay-socket-to-fd',
            ),
        }

    async def wait(self) -> None:
        if not self._started or self._closing is None:
            raise RuntimeError('relay not started')

        close_task = asyncio.create_task(self._closing.wait(), name='unix-relay-close-wait')
        active = set(self._tasks)

        try:
            while active:
                done, _ = await asyncio.wait(
                    active | {close_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )

                if close_task in done:
                    break

                for task in done:
                    if task not in active:
                        continue

                    active.remove(task)

                    exc = task.exception()
                    if exc is not None:
                        raise exc

                    # If the socket->fd side is done, the remote side has closed. There is then no point keeping
                    # fd->socket alive.
                    if task.get_name() == 'unix-relay-socket-to-fd':
                        return

                    # If fd->socket is done normally, stdin hit EOF. Keep reading socket->stdout so the peer can send
                    # its final response.
        finally:
            close_task.cancel()
            await self._cancel_tasks(active | {close_task})

    def close(self) -> None:
        """
        Request shutdown from inside the event loop.

        This is intentionally non-async so signal handlers and sibling tasks can ask the relay to stop. Use
        `await aclose()` when you want to wait for the resources to be released.
        """

        if self._closing is not None:
            self._closing.set()

    async def aclose(self) -> None:
        self.close()
        await self._cancel_tasks(self._tasks)
        self._tasks.clear()

        if self._socket_writer is not None:
            self._socket_writer.close()
            await self._wait_closed(self._socket_writer)
            self._socket_writer = None

        for transport in (self._input_transport, self._output_transport):
            if transport is not None:
                transport.close()

        self._input_transport = None
        self._output_transport = None

    async def _copy_fd_to_socket(
            self,
            fd_reader: asyncio.StreamReader,
            socket_writer: asyncio.StreamWriter,
    ) -> None:
        try:
            while not self._is_closing():
                data = await self._with_timeout(
                    fd_reader.read(self._buffer_size),
                    self._read_timeout,
                    'timed out reading from input fd',
                )
                if not data:
                    break

                socket_writer.write(data)
                await self._with_timeout(
                    socket_writer.drain(),
                    self._write_timeout,
                    'timed out writing to unix socket',
                )

            # Half-close the socket write side, but keep the read side alive so socket->stdout can still receive a final
            # response.
            if socket_writer.can_write_eof():
                socket_writer.write_eof()
                await self._with_timeout(
                    socket_writer.drain(),
                    self._write_timeout,
                    'timed out sending unix socket EOF',
                )
            else:
                socket_writer.close()

        except (asyncio.CancelledError, BrokenPipeError, ConnectionResetError):
            raise

    async def _copy_socket_to_fd(
            self,
            socket_reader: asyncio.StreamReader,
            fd_writer: asyncio.StreamWriter,
    ) -> None:
        try:
            while not self._is_closing():
                data = await self._with_timeout(
                    socket_reader.read(self._buffer_size),
                    self._read_timeout,
                    'timed out reading from unix socket',
                )
                if not data:
                    break

                fd_writer.write(data)
                await self._with_timeout(
                    fd_writer.drain(),
                    self._write_timeout,
                    'timed out writing to output fd',
                )

        except (asyncio.CancelledError, BrokenPipeError, ConnectionResetError):
            raise

    async def _open_fd_reader(self, fd: int) -> asyncio.StreamReader:
        loop = asyncio.get_running_loop()

        # Duplicate so closing the relay does not close the caller's original fd.
        file = os.fdopen(os.dup(fd), 'rb', buffering=0)

        reader = asyncio.StreamReader(limit=self._buffer_size)
        protocol = asyncio.StreamReaderProtocol(reader)

        try:
            transport, _ = await loop.connect_read_pipe(lambda: protocol, file)
        except Exception:
            file.close()
            raise

        self._input_transport = transport
        return reader

    async def _open_fd_writer(self, fd: int) -> asyncio.StreamWriter:
        loop = asyncio.get_running_loop()

        # Duplicate so closing the relay does not close the caller's original fd.
        file = os.fdopen(os.dup(fd), 'wb', buffering=0)

        protocol = asyncio.StreamReaderProtocol(asyncio.StreamReader(limit=self._buffer_size))

        try:
            transport, _ = await loop.connect_write_pipe(lambda: protocol, file)
        except Exception:
            file.close()
            raise

        self._output_transport = transport
        return asyncio.StreamWriter(transport, protocol, None, loop)

    async def _with_timeout(
            self,
            aw: ta.Awaitable[ta.Any],
            timeout: Timeout,
            message: str,
    ) -> ta.Any:
        try:
            if timeout is None:
                return await aw
            return await asyncio.wait_for(aw, timeout)
        except TimeoutError as e:
            raise TimeoutError(message) from e

    async def _cancel_tasks(self, tasks: set[asyncio.Task[ta.Any]]) -> None:
        if not tasks:
            return

        for task in tasks:
            task.cancel()

        try:
            await self._with_timeout(
                asyncio.gather(*tasks, return_exceptions=True),
                self._shutdown_timeout,
                'timed out waiting for relay tasks to stop',
            )
        except TimeoutError:
            # At this point the tasks are cancelled; do not mask the original shutdown path with a secondary timeout.
            pass

    async def _wait_closed(self, writer: asyncio.StreamWriter) -> None:
        try:
            await self._with_timeout(
                writer.wait_closed(),
                self._shutdown_timeout,
                'timed out waiting for socket close',
            )
        except TimeoutError:
            pass

    def _is_closing(self) -> bool:
        return self._closing is not None and self._closing.is_set()


##


async def a_main(argv: ta.Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Relay stdin/stdout to a Unix domain socket.')
    parser.add_argument(
        'socket_path',
        nargs='?',
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), '.acp.sock')),
    )
    parser.add_argument('--buffer-size', type=int, default=64 * 1024)
    parser.add_argument('--connect-timeout', type=parse_timeout, default=10.0)
    parser.add_argument('--read-timeout', type=parse_timeout, default=None, help='Timeout for each read.')
    parser.add_argument('--write-timeout', type=parse_timeout, default=30.0)
    parser.add_argument('--shutdown-timeout', type=parse_timeout, default=5.0)

    ns = parser.parse_args(argv)

    relay = UnixSocketRelay(
        sys.stdin.fileno(),
        sys.stdout.fileno(),
        ns.socket_path,
        buffer_size=ns.buffer_size,
        connect_timeout=ns.connect_timeout,
        read_timeout=ns.read_timeout,
        write_timeout=ns.write_timeout,
        shutdown_timeout=ns.shutdown_timeout,
    )

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, relay.close)
        except NotImplementedError:
            pass

    await relay.run()
    return 0


def main() -> None:
    try:
        raise SystemExit(asyncio.run(a_main(sys.argv[1:])))
    except KeyboardInterrupt:
        raise SystemExit(130) from None


if __name__ == '__main__':
    main()
