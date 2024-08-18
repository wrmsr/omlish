# -*- coding: utf-8 -*-


import asyncio
import os
import pytest
import signal

from aiotk import (
    handle_ctrlc,
    UnixSocketServer,
)


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_ctrlc(event_loop):
    done = asyncio.Future()
    with handle_ctrlc(done, loop=event_loop):
        os.kill(os.getpid(), signal.SIGINT)
        await asyncio.wait_for(done, timeout=1.0)
    assert done.result() is None


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_ctrlc_idempotent(event_loop):
    done = asyncio.Future()
    with handle_ctrlc(done, loop=event_loop):
        os.kill(os.getpid(), signal.SIGINT)
        await asyncio.wait_for(done, timeout=1.0)
        os.kill(os.getpid(), signal.SIGINT)
        os.kill(os.getpid(), signal.SIGINT)
        # NOTE: sleep to yield control to event loop, so it can invoke our
        #       signal handler.
        await asyncio.sleep(0.001)
    assert done.result() is None


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server(event_loop, tempcwd):
    """Basic connectivity check."""

    async def echo(reader, writer):
        try:
            chunk = await reader.read(1024)
            while chunk:
                writer.write(chunk)
                chunk = await reader.read(1024)
        finally:
            writer.close()

    path = './echo.sock'
    async with UnixSocketServer(path, echo, event_loop) as server:
        assert server.path == path
        reader, writer = await asyncio.open_unix_connection(
            path=path,
            loop=event_loop,
        )
        try:
            req = b'FOO'
            writer.write(req)
            rep = await reader.read(1024)
            assert req == rep
        finally:
            writer.close()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_start_while_starting(event_loop, tempcwd):
    """Cannot call start while server is starting."""

    async def noop(reader, writer):
        writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)
    server.start()
    try:
        with pytest.raises(Exception):
            server.start()
    finally:
        await server.wait_started()
        server.close()
        await server.wait_closed()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_start_while_running(event_loop, tempcwd):
    """Cannot call start while server is running."""

    async def noop(reader, writer):
        writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)
    server.start()
    await server.wait_started()
    try:
        with pytest.raises(Exception):
            server.start()
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_wait_started_while_stopped(event_loop, tempcwd):
    """Cannot call wait_started while server is stopped."""

    async def noop(reader, writer):
        writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)
    with pytest.raises(Exception):
        await server.wait_started()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_wait_started_idempotent(event_loop, tempcwd):
    """Can call wait_started as much as you want."""

    async def noop(reader, writer):
        writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)
    server.start()
    try:
        await server.wait_started()
        await server.wait_started()
        await server.wait_started()
    finally:
        await server.wait_started()
        server.close()
        await server.wait_closed()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_wait_closed_idempotent(event_loop, tempcwd):
    """Can call wait_closed as much as you want."""

    async def noop(reader, writer):
        writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)

    # No-op until started.
    await server.wait_closed()
    await server.wait_closed()
    await server.wait_closed()

    server.start()
    await server.wait_started()
    server.close()
    await server.wait_closed()

    # Extra calls are no-ops.
    await server.wait_closed()
    await server.wait_closed()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_close_idempotent(event_loop, tempcwd):
    """Can call wait_closed as much as you want."""

    async def noop(reader, writer):
        writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)

    # No-op until started.
    server.close()
    server.close()
    server.close()

    # Extra calls while closing are no-ops.
    server.start()
    await server.wait_started()
    server.close()
    server.close()
    server.close()
    await server.wait_closed()

    # Extra calls once stopped are no-ops.
    server.close()
    server.close()
    server.close()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_close_while_starting(event_loop, tempcwd):
    """Cannot call close while starting."""

    async def noop(reader, writer):
        writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)

    server.start()
    try:
        with pytest.raises(Exception):
            server.close()
    finally:
        await server.wait_started()
        server.close()
        await server.wait_closed()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_wait_closed_timeout(event_loop, tempcwd):
    """Not finished closing until all sessions complete."""

    # This session will (intentionally) never receive enough data.  After a
    # while, it will get cancelled and (intentionally) ignore the cancellation
    # request to simulate a badly designed session handler.  Once our test
    # verifies this behavior, it will close the client socket, which will
    # finally trigger the shutdown sequence.
    async def noop(reader, writer):
        try:
            await reader.readexactly(1024)
        except asyncio.CancelledError:
            try:
                await reader.readexactly(1024)
            except asyncio.IncompleteReadError:
                pass
        finally:
            writer.close()

    path = './echo.sock'
    server = UnixSocketServer(path, noop, loop=event_loop)
    server.start()
    await server.wait_started()
    try:
        reader, writer = await asyncio.open_unix_connection(
            path=path,
            loop=event_loop,
        )
        try:
            writer.write(b'REQ')
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    reader.readexactly(1), timeout=0.1,
                )
            server.close()
            with pytest.raises(asyncio.TimeoutError):
                await server.wait_closed(timeout=0.1)
        finally:
            writer.close()
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.skipif('sys.platform == "win32"')
@pytest.mark.asyncio
async def test_unix_server_auto_close_connection(event_loop, tempcwd):
    """Connections are closed automatically when sessions finish."""

    # Intentionally do not close the writer.
    async def noop(reader, writer):
        pass

    path = './echo.sock'
    async with UnixSocketServer(path, noop, loop=event_loop) as server:
        reader, writer = await asyncio.open_unix_connection(
            path=path,
            loop=event_loop,
        )
        try:
            with pytest.raises(asyncio.IncompleteReadError):
                await asyncio.wait_for(
                    reader.readexactly(1), timeout=0.1,
                )
            server.close()
            await server.wait_closed()
        finally:
            writer.close()
