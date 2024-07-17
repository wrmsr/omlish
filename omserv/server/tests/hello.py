"""
curl -v localhost:8000
curl -v --http2 localhost:8000
"""
import logging
import time

from omlish import logs
import anyio

from ..config import Config
from ..serving import serve


async def hello_app(scope, recv, send):
    match scope_ty := scope['type']:
        case 'lifespan':
            while True:
                message = await recv()
                if message['type'] == 'lifespan.startup':
                    # Do some startup here!
                    await send({'type': 'lifespan.startup.complete'})

                elif message['type'] == 'lifespan.shutdown':
                    # Do some shutdown here!
                    await send({'type': 'lifespan.shutdown.complete'})
                    return

        case 'http':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/plain'],
                ],
            })

            await send({
                'type': 'http.response.body',
                'body': f'Hello, world! The time is {time.time()}'.encode(),
            })

        case _:
            raise ValueError(f'Unhandled scope type: {scope_ty!r}')


def _main():
    logs.configure_standard_logging(logging.INFO)

    cfg = Config(
        # workers=2,
    )

    backend = 'asyncio'
    # backend = 'trio'

    if cfg.workers > 1:
        from ..multiprocess import serve_multiprocess
        serve_multiprocess(hello_app, cfg)

    else:
        async def _a_main():
            await serve(
                hello_app,
                cfg,
                handle_shutdown_signals=True,  # (backend != 'trio'),
            )

        anyio.run(_a_main, backend=backend)


if __name__ == '__main__':
    _main()
