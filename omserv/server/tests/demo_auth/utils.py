import logging
import typing as ta
import urllib.parse

from omlish import check
from omlish import http as hu


log = logging.getLogger(__name__)


async def stub_lifespan(scope, recv, send):
    while True:
        message = await recv()
        if message['type'] == 'lifespan.startup':
            log.info('Lifespan starting up')
            await send({'type': 'lifespan.startup.complete'})

        elif message['type'] == 'lifespan.shutdown':
            log.info('Lifespan shutting down')
            await send({'type': 'lifespan.shutdown.complete'})
            return


async def start_response(
        send,
        status: int,
        content_type: bytes = hu.consts.CONTENT_TYPE_TEXT_UTF8,
        headers: ta.Sequence[tuple[bytes, bytes]] | None = None,
):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', content_type),
            *(headers or ()),
        ],
    })


async def finish_response(send, body: bytes = b''):
    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def redirect_response(
        send,
        url: str,
        headers: ta.Sequence[tuple[bytes, bytes]] | None = None,
):
    await send({
        'type': 'http.response.start',
        'status': 302,
        'headers': [
            (b'content-type', hu.consts.CONTENT_TYPE_TEXT_UTF8),
            (b'location', url.encode()),
            *(headers or ()),
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': b'',
    })


async def read_body(recv) -> bytes:
    body = b''
    more_body = True
    while more_body:
        message = await recv()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body


async def read_form_body(recv) -> dict[bytes, bytes]:
    body = await read_body(recv)
    dct = urllib.parse.parse_qs(body)  # noqa
    return {k: check.single(v) for k, v in dct.items()}
