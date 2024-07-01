import contextlib
import functools
import socket
import typing as ta

from omlish import check
from omlish import lang
import anyio
import h11
import pytest

from ..config import Config
from ..types import ASGIWrapper
from ..workers import worker_serve
from .sanity import SANITY_BODY
from .sanity import sanity_framework


T = ta.TypeVar('T')


def get_free_port(address: str = '') -> int:
    """Find a free TCP port (entirely at random)"""

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((address, 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_exception_chain(ex: BaseException) -> list[BaseException]:
    cur: BaseException | None = ex
    ret: list[BaseException] = []
    while cur is not None:
        ret.append(cur)
        cur = cur.__cause__
    return ret


async def anyio_eof_to_empty(fn: ta.Callable[..., ta.Awaitable[T]], *args: ta.Any, **kwargs: ta.Any) -> T:
    try:
        return await fn(*args, **kwargs)
    except anyio.EndOfStream:
        return b''


# @pytest.mark.asyncio
@pytest.mark.trio
async def test_server_simple():
    port = get_free_port()
    sev = anyio.Event()

    async def inner():
        async with contextlib.AsyncExitStack() as aes:
            aes.enter_context(lang.defer(sev.set))

            tt = lang.ticking_timeout(5.)
            while True:
                try:
                    conn = await anyio.connect_tcp('127.0.0.1', port)
                except (OSError, ConnectionRefusedError) as e:
                    if not any(isinstance(ce, ConnectionRefusedError) for ce in get_exception_chain(e)):
                        raise
                else:
                    await aes.enter_async_context(conn)
                    break
                await anyio.sleep(.1)
                tt()

            client = h11.Connection(h11.CLIENT)
            await conn.send(check.not_none(client.send(
                h11.Request(
                    method='POST',
                    target='/',
                    headers=[
                        (b'host', b'hypercorn'),
                        (b'connection', b'close'),
                        (b'content-length', b'%d' % len(SANITY_BODY)),
                    ],
                )
            )))
            await conn.send(client.send(h11.Data(data=SANITY_BODY)))  # type: ignore
            await conn.send(client.send(h11.EndOfMessage()))  # type: ignore
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
                        (b'server', b'hypercorn-h11'),
                        (b'connection', b'close'),
                    ],
                    http_version=b'1.1',
                    reason=b'',
                ),
                h11.Data(data=b'Hello & Goodbye'),
                h11.EndOfMessage(headers=[]),
            ]

            await conn.aclose()

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            worker_serve,
            ASGIWrapper(sanity_framework),
            Config(
                bind=(f'127.0.0.1:{port}',)
            ),
            shutdown_trigger=sev.wait,
        ))
        tg.start_soon(inner)
