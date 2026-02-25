"""
TODO:
 - assert no exceptions - hook (/fingers-crossed) log.exception lol
 - h2c test - looks like httpx doesn't do that
  - https://github.com/encode/httpx/issues/503
  - https://python-hyper.org/projects/hyper-h2/en/stable/negotiating-http2.html
 - generic pytest async loop switch...
"""
import contextlib
import functools

import anyio
import h11
import httpx
import pytest
import trio  # noqa

from omlish import check
from omlish import lang
from omlish.asyncs.anyio import eof_to_empty as anyio_eof_to_empty
from omlish.sockets.ports import get_available_port

from ..config import Config
from ..default import serve
from ..types import AsgiWrapper
from .hello import hello_app
from .sanity import SANITY_REQUEST_BODY
from .sanity import SANITY_RESPONSE_BODY
from .sanity import sanity_framework
from .utils import CONNECTION_REFUSED_EXCEPTION_TYPES
from .utils import get_timeout_s
from .utils import headers_time_patch  # noqa
from .utils import is_connection_refused_exception


@pytest.mark.asyncs
async def test_server_simple():
    port = get_available_port()
    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))

            tt = lang.Timeout.of(get_timeout_s())
            while True:
                tt()
                try:
                    conn = await anyio.connect_tcp('127.0.0.1', port)
                except CONNECTION_REFUSED_EXCEPTION_TYPES as e:
                    if not is_connection_refused_exception(e):
                        raise
                    await anyio.sleep(.1)
                    continue
                await aes.enter_async_context(conn)
                break

            client = h11.Connection(h11.CLIENT)
            await conn.send(check.not_none(client.send(
                h11.Request(
                    method='POST',
                    target='/',
                    headers=[
                        (b'host', b'omlicorn'),
                        (b'connection', b'close'),
                        (b'content-length', b'%d' % len(SANITY_REQUEST_BODY)),
                    ],
                ),
            )))
            await conn.send(client.send(h11.Data(data=SANITY_REQUEST_BODY)))
            await conn.send(client.send(h11.EndOfMessage()))
            # await conn.send_eof()

            events = []
            while True:
                event = client.next_event()
                if event == h11.NEED_DATA:
                    data = await anyio_eof_to_empty(conn.receive)
                    client.receive_data(data)
                elif isinstance(event, h11.ConnectionClosed):
                    break
                else:
                    events.append(event)

            assert events == [
                h11.Response(
                    status_code=200,
                    headers=[
                        (b'content-length', b'15'),
                        (b'date', b'Thu, 01 Jan 1970 01:23:20 GMT'),
                        (b'server', b'omlicorn-h11'),
                        (b'connection', b'close'),
                    ],
                    http_version=b'1.1',
                    reason=b'',
                ),
                h11.Data(data=SANITY_RESPONSE_BODY),
                h11.EndOfMessage(headers=[]),
            ]

            await conn.aclose()

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            serve,
            AsgiWrapper(sanity_framework),
            Config(
                bind=(f'127.0.0.1:{port}',),
            ),
            shutdown_trigger=sev.wait,
        ))
        tg.start_soon(inner)


@pytest.mark.asyncs
@pytest.mark.parametrize('use_http2', [False, True])
async def test_httpx_client(use_http2):
    port = get_available_port()
    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))

            tt = lang.Timeout.of(5.)
            while True:
                try:
                    async with httpx.AsyncClient(
                        http1=not use_http2,
                        http2=use_http2,
                    ) as client:
                        resp = await client.post(f'http://127.0.0.1:{port}', content=SANITY_REQUEST_BODY)
                except httpx.ConnectError as e:  # noqa
                    await anyio.sleep(.1)
                    tt()
                    continue
                break

            assert resp.status_code == 200

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            serve,
            AsgiWrapper(sanity_framework),
            Config(
                bind=(f'127.0.0.1:{port}',),
            ),
            shutdown_trigger=sev.wait,
        ))
        tg.start_soon(inner)


@pytest.mark.asyncs
@pytest.mark.parametrize('use_h2c', [False, True])
async def test_curl(use_h2c: bool) -> None:
    port = get_available_port()
    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))

            tt = lang.Timeout.of(get_timeout_s())
            while True:
                tt()
                try:
                    conn = await anyio.connect_tcp('127.0.0.1', port)
                except CONNECTION_REFUSED_EXCEPTION_TYPES as e:
                    if not is_connection_refused_exception(e):
                        raise
                    await anyio.sleep(.1)
                    continue
                await conn.aclose()
                break

            async with await anyio.open_process([
                'curl',
                '-v',
                *(('--http2',) if use_h2c else ()),
                f'http://localhost:{port}',
                '-d', SANITY_REQUEST_BODY.decode(),
            ]) as proc:
                await proc.wait()
                assert proc.returncode == 0

                out = await check.not_none(proc.stdout).receive()
                assert out == SANITY_RESPONSE_BODY

                err = await check.not_none(proc.stderr).receive()
                err_lines = [l.strip() for l in err.decode().splitlines()]
                assert ('> Upgrade: h2c' in err_lines) == use_h2c

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            serve,
            AsgiWrapper(sanity_framework),
            Config(
                bind=(f'127.0.0.1:{port}',),
            ),
            shutdown_trigger=sev.wait,
        ))
        tg.start_soon(inner)


@pytest.mark.asyncs
async def test_curl_h2() -> None:
    port = get_available_port()
    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))

            tt = lang.Timeout.of(get_timeout_s())
            while True:
                tt()
                try:
                    conn = await anyio.connect_tcp('127.0.0.1', port)
                except CONNECTION_REFUSED_EXCEPTION_TYPES as e:
                    if not is_connection_refused_exception(e):
                        raise
                    await anyio.sleep(.1)
                    continue
                await conn.aclose()
                break

            async with await anyio.open_process([
                'curl',
                '-v',
                '--http2',
                f'http://localhost:{port}',
            ]) as proc:
                await proc.wait()
                assert proc.returncode == 0

                out = await check.not_none(proc.stdout).receive()
                assert out.decode().startswith('Hello, world!')

                err = await check.not_none(proc.stderr).receive()
                err_lines = [l.strip() for l in err.decode().splitlines()]
                for p in [
                    '< upgrade: h2c',

                    # darwin:
                    # '* Received 101',
                    # '* Using HTTP2, server supports multiplexing',
                    # '* Connection state changed (HTTP/2 confirmed)',

                    # ci:
                    # '> Connection: Upgrade, HTTP2-Settings'
                    # '* Received 101, Switching to HTTP/2',

                    '< HTTP/2 200',
                ]:
                    assert p in err_lines

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            serve,
            AsgiWrapper(hello_app),
            Config(
                bind=(f'127.0.0.1:{port}',),
            ),
            shutdown_trigger=sev.wait,
        ))
        tg.start_soon(inner)
