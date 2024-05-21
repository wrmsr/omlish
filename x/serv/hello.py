import asyncio
import time

from .config import Config
from .serving import serve


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
                ]
            })

            await send({
                'type': 'http.response.body',
                'body': f'Hello, world! The time is {time.time()}'.encode('utf-8'),
            })

        case _:
            raise ValueError(f'Unhandled scope type: {scope_ty!r}')


def _main():
    cfg = Config()

    async def _asyncio_main():
        await serve(hello_app, cfg)
    asyncio.run(_asyncio_main())


if __name__ == '__main__':
    _main()
