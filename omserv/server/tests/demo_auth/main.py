"""
https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import importlib.resources
import logging
import typing as ta

import anyio
import jinja2

from omlish import lang
from omlish import logs
from omlish.http import consts

from ...config import Config
from ...serving import serve


log = logging.getLogger(__name__)


##


J2_ENV = jinja2.Environment(autoescape=True)


@lang.cached_function
def load_templates() -> ta.Mapping[str, jinja2.Template]:
    ret: dict[str, jinja2.Template] = {}
    for fn in importlib.resources.files(__package__).joinpath('templates').iterdir():
        ret[fn.name] = J2_ENV.from_string(fn.read_text())
    return ret


##


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


##


HANDLERS: dict[tuple[str, str], ta.Any] = {}


def handle(method: str, path: str):
    def inner(fn):
        HANDLERS[(method, path)] = fn
        return fn
    return inner


@handle('GET', '/')
async def handle_get_root(scope, recv, send):
    await start_response(send, 200)
    await finish_response(send, b'hi')


##


async def auth_app(scope, recv, send):
    match scope_ty := scope['type']:
        case 'lifespan':
            await stub_lifespan(scope, recv, send)
            return

        case 'http':
            handler = HANDLERS.get((scope['method'], scope['raw_path'].decode()))

            if handler is not None:
                await handler(scope, recv, send)

            else:
                await start_response(send, 404)
                await finish_response(send)

        case _:
            raise ValueError(f'Unhandled scope type: {scope_ty!r}')


##


def _main():
    logs.configure_standard_logging(logging.INFO)

    load_templates()

    async def _a_main():
        await serve(
            auth_app,
            Config(),
            handle_shutdown_signals=True,
        )

    anyio.run(_a_main)


if __name__ == '__main__':
    _main()
