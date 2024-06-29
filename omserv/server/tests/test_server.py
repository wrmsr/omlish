import asyncio

import h11
import pytest

from ..config import Config
from ..tcpserver import TCPServer
from ..types import ASGIReceiveCallable
from ..types import ASGISendCallable
from ..types import ASGIWrapper
from ..types import Scope
from ..workercontext import WorkerContext
from .asyncio_helpers import MemoryReader
from .asyncio_helpers import MemoryWriter


SANITY_BODY = b"Hello Hypercorn"


async def sanity_framework(
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
) -> None:
    body = b""
    if scope["type"] == "websocket":
        await send({"type": "websocket.accept"})  # type: ignore

    while True:
        event = await receive()
        if event["type"] in {"http.disconnect", "websocket.disconnect"}:
            break
        elif event["type"] == "lifespan.startup":
            await send({"type": "lifspan.startup.complete"})  # type: ignore
        elif event["type"] == "lifespan.shutdown":
            await send({"type": "lifspan.shutdown.complete"})  # type: ignore
        elif event["type"] == "http.request" and event.get("more_body", False):
            body += event["body"]
        elif event["type"] == "http.request" and not event.get("more_body", False):
            body += event["body"]
            assert body == SANITY_BODY
            response = b"Hello & Goodbye"
            content_length = len(response)
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-length", str(content_length).encode())],
                }
            )
            await send({"type": "http.response.body", "body": response, "more_body": False})
            break
        elif event["type"] == "websocket.receive":
            assert event["bytes"] == SANITY_BODY
            await send({"type": "websocket.send", "text": "Hello & Goodbye"})  # type: ignore


@pytest.mark.asyncio
async def test_server_asyncio():
    event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    server = TCPServer(
        ASGIWrapper(sanity_framework),
        event_loop,
        Config(),
        WorkerContext(None),
        MemoryReader(),  # type: ignore
        MemoryWriter(),  # type: ignore
    )
    task = event_loop.create_task(server.run())
    client = h11.Connection(h11.CLIENT)
    await server.reader.send(  # type: ignore
        client.send(
            h11.Request(
                method="POST",
                target="/",
                headers=[
                    (b"host", b"hypercorn"),
                    (b"connection", b"close"),
                    (b"content-length", b"%d" % len(SANITY_BODY)),
                ],
            )
        )
    )
    await server.reader.send(client.send(h11.Data(data=SANITY_BODY)))  # type: ignore
    await server.reader.send(client.send(h11.EndOfMessage()))  # type: ignore
    events = []
    while True:
        event = client.next_event()
        if event == h11.NEED_DATA:
            data = await server.writer.receive()  # type: ignore
            client.receive_data(data)
        elif isinstance(event, h11.ConnectionClosed):
            break
        else:
            events.append(event)

    assert events == [
        h11.Response(
            status_code=200,
            headers=[
                (b"content-length", b"15"),
                (b"date", b"Thu, 01 Jan 1970 01:23:20 GMT"),
                (b"server", b"hypercorn-h11"),
                (b"connection", b"close"),
            ],
            http_version=b"1.1",
            reason=b"",
        ),
        h11.Data(data=b"Hello & Goodbye"),
        h11.EndOfMessage(headers=[]),
    ]
    server.reader.close()  # type: ignore
    await task


@pytest.mark.trio
async def test_server_trio():
    pass
