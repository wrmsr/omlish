import logging
import typing as ta

import anyio

from omlish import logs

from ..config import Config
from ..serving import serve


HANDLERS: dict[tuple[str, str], ta.Any] = {}


def handle(method: str, path: str):
    def inner(fn):
        HANDLERS[(method, path)] = fn
        return fn
    return inner


@handle('GET', '/')
async def handle_get_root(scope, recv, send):
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'text/plain'],
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': b'hi',
    })


async def auth_app(scope, recv, send):
    match scope_ty := scope['type']:
        case 'lifespan':
            while True:
                message = await recv()
                if message['type'] == 'lifespan.startup':
                    await send({'type': 'lifespan.startup.complete'})
                    return

                elif message['type'] == 'lifespan.shutdown':
                    # Do some shutdown here!
                    await send({'type': 'lifespan.shutdown.complete'})
                    return

        case 'http':
            handler = HANDLERS.get((scope['method'], scope['raw_path'].decode()))

            if handler is not None:
                await handler(scope, recv, send)

            else:
                await send({
                    'type': 'http.response.start',
                    'status': 404,
                    'headers': [
                        [b'content-type', b'text/plain'],
                    ],
                })

                await send({
                    'type': 'http.response.body',
                    'body': b'',
                })

        case _:
            raise ValueError(f'Unhandled scope type: {scope_ty!r}')


def _main():
    logs.configure_standard_logging(logging.INFO)

    async def _a_main():
        await serve(
            auth_app,
            Config(),
            handle_shutdown_signals=True,
        )

    anyio.run(_a_main)


if __name__ == '__main__':
    _main()
