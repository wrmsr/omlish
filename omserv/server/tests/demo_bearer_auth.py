import logging

import anyio

from omlish import logs

from ..config import Config
from ..serving import serve
from .hello import hello_app


BASIC_AUTH_TOKEN = b'blahblah'
BASIC_AUTH_HEADER = b'Bearer ' + BASIC_AUTH_TOKEN


def authed_app(app):
    async def handle(scope, recv, send):
        if scope['type'] == 'http':
            hdrs = dict(scope['headers'])
            auth = hdrs.get(b'authorization')
            if auth != BASIC_AUTH_HEADER:
                await send({
                    'type': 'http.response.start',
                    'status': 401,
                    'headers': [
                        [b'content-type', b'text/plain'],
                    ],
                })
                await send({
                    'type': 'http.response.body',
                    'body': b'',
                })
                return

        await app(scope, recv, send)

    return handle


def _main():
    logs.configure_standard_logging(logging.INFO)

    async def _a_main():
        await serve(
            authed_app(hello_app),
            Config(),
            handle_shutdown_signals=True,
        )

    anyio.run(_a_main)


if __name__ == '__main__':
    _main()
