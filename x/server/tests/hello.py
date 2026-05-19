"""
curl -v localhost:8000
curl -v --http2 localhost:8000
"""
import importlib.resources
import logging
import time

import anyio
import jinja2

from omlish.logs import all as logs

from ..config import Config
from ..default import serve


JINJA_ENV = jinja2.Environment(autoescape=True)
HELLO_TMPL = JINJA_ENV.from_string(importlib.resources.files(__package__).joinpath('hello.j2').read_text())


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
                'body': HELLO_TMPL.render(now_str=str(time.time())).encode(),
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

    if cfg.workers:
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
