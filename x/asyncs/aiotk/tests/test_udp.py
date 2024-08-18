# -*- coding: utf-8 -*-


import asyncio
import pytest

from aiotk import cancel, udp_server, EnsureDone, AsyncExitStack


@pytest.mark.asyncio
async def test_udp(event_loop):
    """Simple UDP echo service."""

    host = '127.0.0.1'
    server_port = 5555
    client_port = 5556

    async def echo_server(iqueue, oqueue, loop):
        """UDP echo server."""

        try:
            while True:
                peer, data = await iqueue.get()
                assert peer == (host, client_port)
                await oqueue.put((peer, data))
        except asyncio.CancelledError:
            pass

    async def echo_client(iqueue, oqueue, loop):
        """UDP echo client."""

        # Repeatedly send until the server ACKs.
        item = None
        while item is None:
            try:
                item = iqueue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.5, loop=loop)
                await oqueue.put(((host, server_port), b'PING'))

        peer, data = item
        assert peer == (host, server_port)
        assert data == b'PING'

    async with AsyncExitStack() as stack:
        server = await stack.enter_context(EnsureDone(
            udp_server(host, server_port, echo_server), loop=event_loop,
        ))
        client = await stack.enter_context(EnsureDone(
            udp_server(host, client_port, echo_client), loop=event_loop,
        ))
        await asyncio.wait_for(client, timeout=5.0, loop=event_loop)
        await cancel(server, loop=event_loop)

    assert client.result() is None
    assert server.result() is None
