#!/usr/bin/env python3
"""Unix socket-based notification system for CLI tools."""
import argparse
import asyncio
import os
import socket
import sys
import time

from omlish.sockets.peercreds import PeerCred
from omlish.sockets.peercreds import get_unix_socket_peer_cred


##


def _default_socket_dir() -> str:
    return os.path.join(os.path.dirname(__file__), '.socks')


def _get_socket_path(socket_dir: str, pid: int | None = None) -> str:
    """Get the socket file path for a given PID (or current process)."""

    if pid is None:
        pid = os.getpid()
    return os.path.join(socket_dir, f'{pid}-{time.time_ns()}.sock')


def _ensure_socket_dir(socket_dir: str) -> None:
    """Create socket directory if it doesn't exist."""

    os.makedirs(socket_dir, exist_ok=True)


def _iter_socket_files(socket_dir: str) -> list[str]:
    return [
        filename
        for filename in os.listdir(socket_dir)
        if filename.endswith('.sock')
    ]


def _iter_pid_socket_files(socket_dir: str, pid: int) -> list[str]:
    prefix = f'{pid}-'
    return [
        filename
        for filename in os.listdir(socket_dir)
        if filename.startswith(prefix) and filename.endswith('.sock')
    ]


def _parse_socket_pid(filename: str) -> int:
    return int(filename[:-5].split('-', 1)[0])


##


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, queue: asyncio.Queue) -> None:
    """Handle incoming notifications from a client."""

    peer_cred: PeerCred | None = None

    try:
        sock = writer.get_extra_info('socket')
        peer_cred = get_unix_socket_peer_cred(sock)

        if peer_cred is not None:
            print(f'Notifier {peer_cred} connected')
        else:
            print('Notifier connected')

        while True:
            try:
                data = await asyncio.wait_for(reader.readuntil(b'\n'), timeout=5.0)
            except asyncio.TimeoutError:
                break
            except asyncio.IncompleteReadError as e:
                data = e.partial
                if not data:
                    break

            if not data:
                break

            payload = data.decode('utf-8').rstrip('\n')
            await queue.put(payload)

            try:
                writer.write(b'\n')
                await asyncio.wait_for(writer.drain(), timeout=5.0)
            except asyncio.TimeoutError:
                break

    except Exception as e:  # noqa
        pass

    finally:
        try:
            if peer_cred is not None:
                print(f'Notifier {peer_cred} disconnected')
            else:
                print('Notifier disconnected')
        except Exception:  # noqa
            pass

        try:
            writer.close()
            await writer.wait_closed()

        except Exception:  # noqa
            pass


async def _run_server(socket_path: str, queue: asyncio.Queue) -> asyncio.Server:
    """Start the unix socket server."""

    server = await asyncio.start_unix_server(
        lambda r, w: _handle_client(r, w, queue),
        path=socket_path,
    )
    return server


##


async def _chat_loop(socket_path: str) -> None:
    queue: asyncio.Queue[tuple[str, str | None]] = asyncio.Queue()
    server_queue: asyncio.Queue[str] = asyncio.Queue()
    server = await _run_server(socket_path, server_queue)

    loop = asyncio.get_running_loop()

    # Bridge server notifications into the main queue
    async def _forward_notifications() -> None:
        while True:
            payload = await server_queue.get()
            await queue.put(('notify', payload))

    forward_task = asyncio.create_task(_forward_notifications())

    def _stdin_ready() -> None:
        line = sys.stdin.readline()
        if not line:
            queue.put_nowait(('quit', None))
            return

        line = line.rstrip('\n')

        try:
            os.utime(socket_path, None)
        except OSError:
            pass

        if line == '/quit':
            queue.put_nowait(('quit', None))
        else:
            queue.put_nowait(('input', line))

    loop.add_reader(sys.stdin.fileno(), _stdin_ready)

    try:
        print('Chat started. Type /quit to exit.')
        print('> ', end='', flush=True)

        while True:
            kind, value = await queue.get()

            if kind == 'input':
                print(f'You said: {value}')
                print('> ', end='', flush=True)

            elif kind == 'notify':
                print(f'\nNotification: {value}')
                print('> ', end='', flush=True)

            elif kind == 'quit':
                break

    finally:
        loop.remove_reader(sys.stdin.fileno())

        forward_task.cancel()

        server.close()
        await server.wait_closed()

        if os.path.exists(socket_path):
            os.unlink(socket_path)


def _chat_command(
        *,
        socket_dir: str | None = None,
) -> int:
    """Execute the chat command."""

    if socket_dir is None:
        socket_dir = _default_socket_dir()
    _ensure_socket_dir(socket_dir)
    socket_path = _get_socket_path(socket_dir)

    # Remove stale socket file if it exists
    if os.path.exists(socket_path):
        os.unlink(socket_path)

    try:
        asyncio.run(_chat_loop(socket_path))
        return 0

    except KeyboardInterrupt:
        print('\nExiting...')
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        return 0

    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        return 1


##


def _send_notification(
        socket_path: str,
        payload: str,
        *,
        nowait: bool = False,
        timeout: float | None = 5,
) -> str | None:
    """Send a notification to a socket. Returns the ack line, or None in nowait mode."""

    deadline = None if timeout is None else (time.monotonic() + timeout)

    def _remaining_timeout() -> float | None:
        if deadline is None:
            return None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('notification timed out')
        return remaining

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.settimeout(_remaining_timeout())
        sock.connect(socket_path)

        sock.settimeout(_remaining_timeout())
        sock.sendall(f'{payload}\n'.encode('utf-8'))

        if nowait:
            return ''

        chunks: list[bytes] = []
        while True:
            sock.settimeout(_remaining_timeout())
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if b'\n' in chunk:
                break

        data = b''.join(chunks)
        line, _, _rest = data.partition(b'\n')
        ack = line.decode('utf-8').rstrip('\n')
        return ack

    finally:
        sock.close()


#


async def _async_send_notification(
        socket_path: str,
        payload: str,
        *,
        nowait: bool = False,
        timeout: float | None = 5,
) -> str | None:
    """Send a notification to a socket asynchronously. Returns the ack line, or None in nowait mode."""

    deadline = None if timeout is None else (time.monotonic() + timeout)

    def _remaining_timeout() -> float | None:
        if deadline is None:
            return None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('notification timed out')
        return remaining

    reader: asyncio.StreamReader | None = None
    writer: asyncio.StreamWriter | None = None
    try:
        connect_coro = asyncio.open_unix_connection(socket_path)
        remaining = _remaining_timeout()
        if remaining is None:
            reader, writer = await connect_coro
        else:
            reader, writer = await asyncio.wait_for(connect_coro, timeout=remaining)

        writer.write(f'{payload}\n'.encode('utf-8'))
        remaining = _remaining_timeout()
        if remaining is None:
            await writer.drain()
        else:
            await asyncio.wait_for(writer.drain(), timeout=remaining)

        if nowait:
            return None

        chunks: list[bytes] = []
        while True:
            remaining = _remaining_timeout()
            recv_coro = reader.read(4096)
            if remaining is None:
                chunk = await recv_coro
            else:
                chunk = await asyncio.wait_for(recv_coro, timeout=remaining)

            if not chunk:
                break
            chunks.append(chunk)
            if b'\n' in chunk:
                break

        data = b''.join(chunks)
        line, _, _rest = data.partition(b'\n')
        ack = line.decode('utf-8').rstrip('\n')
        if ack.strip():
            print(ack)
        return ack

    finally:
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass


##


def _notify_command(
        payload: str,
        *,
        socket_dir: str | None = None,
        pid: int | None = None,
        latest: bool = False,
) -> int:
    """Execute the notify command."""

    if socket_dir is None:
        socket_dir = _default_socket_dir()
    _ensure_socket_dir(socket_dir)
    _ensure_socket_dir(socket_dir)

    if pid:
        # Notify specific PID
        socket_files = _iter_pid_socket_files(socket_dir, pid)
        if not socket_files:
            print(f'Socket for PID {pid} not found', file=sys.stderr)
            return 1

        for filename in socket_files:
            socket_path = os.path.join(socket_dir, filename)
            if (ack := _send_notification(socket_path, payload)) is not None:
                if (ack := ack.strip()):
                    print(ack)
                return 0

        print(f'Failed to send notification to PID {pid}', file=sys.stderr)
        return 1

    elif latest:
        # Notify the most recently modified socket
        socket_files = []
        for filename in _iter_socket_files(socket_dir):
            path = os.path.join(socket_dir, filename)
            try:
                mtime = os.path.getmtime(path)
                socket_files.append((mtime, path, filename))
            except OSError:
                continue

        if not socket_files:
            print('No socket files found', file=sys.stderr)
            return 1

        # Sort by mtime descending
        socket_files.sort(reverse=True, key=lambda x: x[0])

        for _, path, filename in socket_files:
            if (ack := _send_notification(path, payload)) is not None:
                pid = _parse_socket_pid(filename)
                print(pid)
                if (ack := ack.strip()):
                    print(ack)
                return 0

        print('Failed to send notification to any socket', file=sys.stderr)
        return 1

    else:
        # Notify all sockets
        success_pids = []

        for filename in _iter_socket_files(socket_dir):
            path = os.path.join(socket_dir, filename)
            if (ack := _send_notification(path, payload)) is not None:
                pid = _parse_socket_pid(filename)
                print(pid)
                print(ack)
                success_pids.append(pid)

        if success_pids:
            return 0
        else:
            return 1


##


def _cleanup_command(
        *,
        socket_dir: str | None = None,
        min_age: float | None = 5.,
) -> int:
    """Execute the cleanup command."""

    if socket_dir is None:
        socket_dir = _default_socket_dir()
    _ensure_socket_dir(socket_dir)

    current_time = time.time()

    print(f'{"File":<40} {"Created":<20} {"Modified":<20} {"Status":<10}')
    print('-' * 89)

    for filename in _iter_socket_files(socket_dir):
        path = os.path.join(socket_dir, filename)

        try:
            stat_info = os.stat(path)
            ctime = stat_info.st_ctime
            mtime = stat_info.st_mtime
            age = current_time - mtime

            # Skip if too young (to avoid race condition)
            if age < min_age:
                continue

            # Try to connect
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect(path)
                sock.close()
                # Connection succeeded, socket is alive
                status = 'alive'

            except Exception:
                # Connection failed, remove stale socket
                os.unlink(path)
                status = 'removed'

            ctime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime))
            mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            print(f'{filename:<40} {ctime_str:<20} {mtime_str:<20} {status:<10}')

        except OSError:
            continue

    return 0


##


def _main() -> None:
    """Main entry point."""

    parser = argparse.ArgumentParser(description='Unix socket notification system')
    parser.add_argument('--socket-dir')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Chat command
    subparsers.add_parser('chat')

    # Notify command
    notify_parser = subparsers.add_parser('notify')
    notify_parser.add_argument('payload')
    notify_group = notify_parser.add_mutually_exclusive_group()
    notify_group.add_argument('-p', '--pid', type=int)
    notify_group.add_argument('-l', '--latest', action='store_true')

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup')
    cleanup_parser.add_argument('-M', '--min-age', type=float, default=5)

    args = parser.parse_args()

    if args.command == 'chat':
        sys.exit(_chat_command(
            socket_dir=args.socket_dir,
        ))
    elif args.command == 'notify':
        sys.exit(_notify_command(
            args.payload,
            socket_dir=args.socket_dir,
        ))
    elif args.command == 'cleanup':
        sys.exit(_cleanup_command(
            socket_dir=args.socket_dir,
            min_age=args.min_age,
        ))


if __name__ == '__main__':
    _main()
