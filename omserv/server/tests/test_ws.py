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
import pytest
import wsproto

from omlish import lang
from omlish.asyncs.anyio import eof_to_empty as anyio_eof_to_empty
from omlish.sockets.ports import get_available_port

from ..config import Config
from ..default import serve
from ..types import AsgiWrapper
from .sanity import SANITY_REQUEST_BODY
from .sanity import sanity_framework
from .utils import CONNECTION_REFUSED_EXCEPTION_TYPES
from .utils import get_timeout_s
from .utils import headers_time_patch  # noqa
from .utils import is_connection_refused_exception


@pytest.mark.asyncs
async def test_server_websocket():
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

            client = wsproto.WSConnection(wsproto.ConnectionType.CLIENT)
            await conn.send(client.send(wsproto.events.Request(host='omlicorn', target='/')))

            client.receive_data(await anyio_eof_to_empty(conn.receive))
            assert list(client.events()) == [
                wsproto.events.AcceptConnection(
                    extra_headers=[
                        (b'date', b'Thu, 01 Jan 1970 01:23:20 GMT'),
                        (b'server', b'omlicorn-h11'),
                    ],
                ),
            ]

            await conn.send(client.send(wsproto.events.BytesMessage(data=SANITY_REQUEST_BODY)))
            client.receive_data(await anyio_eof_to_empty(conn.receive))
            assert list(client.events()) == [wsproto.events.TextMessage(data='Hello & Goodbye')]

            await conn.send(client.send(wsproto.events.CloseConnection(code=1000)))
            client.receive_data(await anyio_eof_to_empty(conn.receive))
            assert list(client.events()) == [wsproto.events.CloseConnection(code=1000, reason='')]

            # assert conn.is_closed

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
