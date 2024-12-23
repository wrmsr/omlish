import trio

from omlish.http.asgi import stub_lifespan
from omserv.server import Config
from omserv.server import serve


async def _a_main() -> None:
    async def app(scope, recv, send):
        if scope['type'] == 'lifespan':
            await stub_lifespan(scope, recv, send)

        elif scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    (b'content-type', b'text/plain'),
                ],
            })

            await send({
                'type': 'http.response.body',
                'body': 'hi\n'.encode('utf-8'),
            })

    await serve(
        app,
        Config(),
    )


if __name__ == '__main__':
    trio.run(_a_main)