# -*- coding: utf-8 -*-


import asyncio
import pytest

from aiotk import (
    TCPServer,
    tcp_server,
)


class Echo(asyncio.Protocol):
    """Demo from the asyncio documentation."""

    def __init__(self):
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data):
        self._transport.write(data)
        self._transport.close()

    def connection_lost(self, exc):
        pass


@pytest.mark.asyncio
async def test_tcp_server_fn(event_loop, unused_tcp_port):
    """Basic connectivity check."""

    host = '127.0.0.1'
    port = unused_tcp_port

    # Start the TCP server.
    task = event_loop.create_task(tcp_server(
        protocol_factory=Echo,
        host=host, port=port, loop=event_loop,
    ))

    try:
        # Wait until the server is responsive.
        await asyncio.sleep(0.1, loop=event_loop)

        # Check connectivity.
        reader, writer = await asyncio.open_connection(
            host=host,
            port=port,
            loop=event_loop,
        )
        try:
            message = b'Hello!'
            writer.write(message)
            assert (await reader.readline()) == message
        finally:
            writer.close()
    finally:
        task.cancel()
        await asyncio.wait({task}, loop=event_loop)


@pytest.mark.asyncio
async def test_tcp_server(event_loop):
    """Basic connectivity check."""

    host = '127.0.0.1'

    async def echo(reader, writer):
        try:
            chunk = await reader.read(1024)
            while chunk:
                writer.write(chunk)
                chunk = await reader.read(1024)
        finally:
            writer.close()

    async with TCPServer(host, 0, echo, event_loop) as server:
        assert server.host == host
        assert server.port > 0
        reader, writer = await asyncio.open_connection(
            host=host,
            port=server.port,
            loop=event_loop,
        )
        try:
            req = b'FOO'
            writer.write(req)
            rep = await reader.read(1024)
            assert req == rep
        finally:
            writer.close()


@pytest.mark.asyncio
async def test_tcp_server_start_while_starting(event_loop, unused_tcp_port):
    """Cannot call start while server is starting."""

    host = '127.0.0.1'
    port = unused_tcp_port

    async def noop(reader, writer):
        writer.close()

    server = TCPServer(host, port, noop, loop=event_loop)
    server.start()
    try:
        with pytest.raises(Exception):
            server.start()
    finally:
        await server.wait_started()
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_tcp_server_start_while_running(event_loop, unused_tcp_port):
    """Cannot call start while server is running."""

    host = '127.0.0.1'
    port = unused_tcp_port

    async def noop(reader, writer):
        writer.close()

    server = TCPServer(host, port, noop, loop=event_loop)
    server.start()
    await server.wait_started()
    try:
        with pytest.raises(Exception):
            server.start()
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_tcp_server_wait_started_while_stopped(event_loop,
                                                     unused_tcp_port):
    """Cannot call wait_started while server is stopped."""

    host = '127.0.0.1'
    port = unused_tcp_port

    async def noop(reader, writer):
        writer.close()

    server = TCPServer(host, port, noop, loop=event_loop)
    with pytest.raises(Exception):
        await server.wait_started()


@pytest.mark.asyncio
async def test_tcp_server_wait_started_idempotent(event_loop, unused_tcp_port):
    """Can call wait_started as much as you want."""

    host = '127.0.0.1'
    port = unused_tcp_port

    async def noop(reader, writer):
        writer.close()

    server = TCPServer(host, port, noop, loop=event_loop)
    server.start()
    try:
        await server.wait_started()
        await server.wait_started()
        await server.wait_started()
    finally:
        await server.wait_started()
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_tcp_server_wait_closed_idempotent(event_loop, unused_tcp_port):
    """Can call wait_closed as much as you want."""

    host = '127.0.0.1'
    port = unused_tcp_port

    async def noop(reader, writer):
        writer.close()

    server = TCPServer(host, port, noop, loop=event_loop)

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


@pytest.mark.asyncio
async def test_tcp_server_close_idempotent(event_loop, unused_tcp_port):
    """Can call wait_closed as much as you want."""

    host = '127.0.0.1'
    port = unused_tcp_port

    async def noop(reader, writer):
        writer.close()

    server = TCPServer(host, port, noop, loop=event_loop)

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


@pytest.mark.asyncio
async def test_tcp_server_close_while_starting(event_loop, unused_tcp_port):
    """Cannot call close while starting."""

    host = '127.0.0.1'
    port = unused_tcp_port

    async def noop(reader, writer):
        writer.close()

    server = TCPServer(host, port, noop, loop=event_loop)

    server.start()
    try:
        with pytest.raises(Exception):
            server.close()
    finally:
        await server.wait_started()
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_tcp_server_wait_closed_timeout(event_loop, unused_tcp_port):
    """Not finished closing until all sessions complete."""

    host = '127.0.0.1'
    port = unused_tcp_port

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

    server = TCPServer(host, port, noop, loop=event_loop)
    server.start()
    await server.wait_started()
    try:
        reader, writer = await asyncio.open_connection(
            host=host,
            port=port,
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


@pytest.mark.asyncio
async def test_tcp_server_auto_close_connection(event_loop, unused_tcp_port):
    """Connections are closed automatically when sessions finish."""

    host = '127.0.0.1'
    port = unused_tcp_port

    # Intentionally do not close the writer.
    async def noop(reader, writer):
        pass

    async with TCPServer(host, port, noop, loop=event_loop) as server:
        reader, writer = await asyncio.open_connection(
            host=host,
            port=port,
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
