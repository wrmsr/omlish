# ruff: noqa: UP006 UP007 UP043 UP045
import errno
import socket
import typing as ta
import urllib.parse

import pytest

from .....lite.check import check
from ..client import CoroHttpClientConnection
from ..client import CoroHttpClientResponse
from ..io import CoroHttpClientIo


##


def run_httpx(
        url: str,
) -> None:
    import asyncio

    import httpx

    async def inner():
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', url) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    print(chunk.decode('utf-8'), end='')

    asyncio.run(inner())


def run_urllib(
        url: str,
) -> None:
    import urllib.request

    req = urllib.request.Request(url)  # noqa

    with urllib.request.urlopen(req) as resp:  # noqa
        print(resp.read())


def run_stdlib(
        url: str,
) -> None:
    conn_cls = __import__('http.client').client.HTTPConnection

    ups = urllib.parse.urlparse(url)
    conn = conn_cls(ups.hostname)

    conn.request('GET', ups.path or '/')
    r1 = conn.get_response() if hasattr(conn, 'get_response') else conn.getresponse()  # noqa
    print((r1.status, r1.reason))

    # data1 = r1.read()

    while chunk := r1.read(200):
        print(repr(chunk))


def run_coro(
        url: str,
) -> None:
    conn_cls = CoroHttpClientConnection

    ups = urllib.parse.urlparse(url)
    conn = conn_cls(check.not_none(ups.hostname))

    sock: ta.Optional[socket.socket] = None
    sock_file: ta.Optional[ta.Any] = None

    def handle_io(o: CoroHttpClientIo.Io) -> ta.Any:
        nonlocal sock
        nonlocal sock_file

        if isinstance(o, CoroHttpClientIo.ConnectIo):
            check.none(sock)
            sock = socket.create_connection(*o.args, **(o.kwargs or {}))

            # Might fail in OSs that don't implement TCP_NODELAY
            try:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except OSError as e:
                if e.errno != errno.ENOPROTOOPT:
                    raise

            sock_file = sock.makefile('rb')

            return None

        elif isinstance(o, CoroHttpClientIo.CloseIo):
            check.not_none(sock).close()
            return None

        elif isinstance(o, CoroHttpClientIo.WriteIo):
            check.not_none(sock).sendall(o.data)
            return None

        elif isinstance(o, CoroHttpClientIo.ReadIo):
            if (sz := o.sz) is not None:
                return check.not_none(sock_file).read(sz)
            else:
                return check.not_none(sock_file).read()

        elif isinstance(o, CoroHttpClientIo.ReadLineIo):
            return check.not_none(sock_file).readline(o.sz)

        else:
            raise TypeError(o)

    resp: ta.Optional[CoroHttpClientResponse] = None

    def get_resp():
        nonlocal resp
        resp = yield from conn.get_response()

    def print_resp():
        d = yield from check.not_none(resp).read()
        print(d)

    for f in [
        conn.connect,
        lambda: conn.request('GET', ups.path or '/'),
        get_resp,
        print_resp,
        conn.close,
    ]:
        g = f()
        i = None
        while True:
            try:
                o = g.send(i)
            except StopIteration:
                break
            i = handle_io(o)


@pytest.mark.online
def test_client() -> None:
    # run = run_httpx
    # run = run_urllib
    # run = run_stdlib
    run = run_coro

    for url in [
        'http://www.example.com',
        'https://www.baidu.com',
        'https://anglesharp.azurewebsites.net/Chunked',
    ]:
        run(url)
