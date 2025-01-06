import functools
import socket
import typing as ta

import anyio.to_thread
import pytest

from ... import lang
from .. import anyio as anu


@pytest.fixture
def server_sock() -> ta.Generator[socket.socket, None, None]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.bind(('localhost', 0))
    sock.listen()
    yield sock
    sock.close()


@pytest.fixture
def server_addr(server_sock: socket.socket) -> tuple[str, int]:
    return server_sock.getsockname()[:2]


@pytest.mark.asyncs
async def test_send_receive_all_backends(
        server_sock: socket.socket,
        server_addr: tuple[str, int],
) -> None:
    async with await anyio.connect_tcp(*server_addr) as stream:
        client, _ = server_sock.accept()
        await stream.send(b'blah')
        request = client.recv(100)
        client.sendall(request[::-1])
        response = await stream.receive()
        client.close()

    assert response == b'halb'


async def _test_send_receive(
        server_sock: socket.socket,
        server_addr: tuple[str, int],
) -> None:
    async with await anyio.connect_tcp(*server_addr) as stream:
        client, _ = server_sock.accept()
        await stream.send(b'blah')
        request = client.recv(100)
        client.sendall(request[::-1])
        response = await stream.receive()
        client.close()

    assert response == b'halb'


@pytest.mark.asyncs('asyncio')
async def test_send_receive_asyncio(
        server_sock: socket.socket,
        server_addr: tuple[str, int],
) -> None:
    await _test_send_receive(server_sock, server_addr)


@pytest.mark.asyncs('trio')
async def test_send_receive_trio(
        server_sock: socket.socket,
        server_addr: tuple[str, int],
) -> None:
    await _test_send_receive(server_sock, server_addr)


@pytest.mark.asyncs('asyncio')
async def test_lazy_fn():
    c = 0

    async def fn():
        nonlocal c
        c += 1
        return 420

    lfn = anu.LazyFn(fn)

    assert c == 0
    assert await lfn.get() == 420
    assert c == 1
    assert await lfn.get() == 420
    assert c == 1


@pytest.mark.asyncs('asyncio')
async def test_lazy_fn2():
    c = 0

    def fn():
        nonlocal c
        c += 1
        return 420

    lfn = anu.LazyFn(lang.as_async(fn))

    assert c == 0
    assert await lfn.get() == 420
    assert c == 1
    assert await lfn.get() == 420
    assert c == 1


@pytest.mark.asyncs('asyncio')
@pytest.mark.drain_asyncio
async def test_lazy_fn3():
    c = 0

    def fn():
        nonlocal c
        c += 1
        return 420

    lfn = anu.LazyFn(functools.partial(anyio.to_thread.run_sync, fn))

    assert c == 0
    assert await lfn.get() == 420
    assert c == 1
    assert await lfn.get() == 420
    assert c == 1


@pytest.mark.asyncs
# @pytest.mark.asyncio
# @pytest.mark.drain_asyncio
async def test_cancel():
    await anu.gather(
        functools.partial(anyio.sleep, .02),
        functools.partial(anyio.sleep, .01),
        take_first=True,
    )
