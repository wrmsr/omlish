import socket
import typing as ta

import anyio
import pytest


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


@pytest.mark.asyncio
async def test_send_receive(
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
