import logging

from omlish.http import consts


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


async def start_response(send, status: int, content_type: bytes = consts.CONTENT_TYPE_TEXT_UTF8):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            [b'content-type', content_type],
        ],
    })


async def finish_response(send, body: bytes = b''):
    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def redirect_response(send, url: str):
    await send({
        'type': 'http.response.start',
        'status': 302,
        'headers': [
            [b'content-type', consts.CONTENT_TYPE_TEXT_UTF8],
            [b'location', url.encode()],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': b'',
    })
