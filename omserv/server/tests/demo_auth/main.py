"""
https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import logging
import typing as ta
import urllib.parse

import anyio

from omlish import check
from omlish import logs
from omlish.http import consts

from ...config import Config
from ...serving import serve
from .j2 import j2_helper
from .j2 import load_templates
from .j2 import render_template
from .users import USERS
from .utils import finish_response
from .utils import redirect_response
from .utils import start_response
from .utils import stub_lifespan


log = logging.getLogger(__name__)


##


@j2_helper
def url_for(s: str) -> str:
    return f'http://localhost:8000/{s}'


##


HANDLERS: dict[tuple[str, str], ta.Any] = {}


def handle(method: str, path: str):
    def inner(fn):
        HANDLERS[(method, path)] = fn
        return fn
    return inner


##


def login_required(fn):
    return fn


##


@handle('GET', '/')
async def handle_get_index(scope, recv, send):
    await start_response(send, 200, consts.CONTENT_TYPE_HTML_UTF8)
    await finish_response(send, render_template('index.html'))


#


@handle('GET', '/profile')
@login_required
async def handle_get_profile(scope, recv, send):
    await start_response(send, 200, consts.CONTENT_TYPE_HTML_UTF8)
    await finish_response(send, render_template('profile.html'))


#


@handle('GET', '/login')
async def handle_get_login(scope, recv, send):
    await start_response(send, 200, consts.CONTENT_TYPE_HTML_UTF8)
    await finish_response(send, render_template('login.html'))


@handle('POST', '/login')
async def handle_post_login(scope, recv, send):
    raise NotImplementedError


#

@handle('GET', '/signup')
async def handle_get_signup(scope, recv, send):
    await start_response(send, 200, consts.CONTENT_TYPE_HTML_UTF8)
    await finish_response(send, render_template('signup.html'))


@handle('POST', '/signup')
async def handle_post_signup(scope, recv, send):
    body = b''
    more_body = True
    while more_body:
        message = await recv()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    dct = urllib.parse.parse_qs(body)  # noqa
    email = check.single(dct[b'email']).decode()
    password = check.single(dct[b'password']).decode()
    name = check.single(dct[b'name']).decode()

    USERS.create(
        email=email,
        password=password,
        name=name,
    )

    await redirect_response(send, url_for('login'))


#


@handle('GET', '/logout')
@login_required
async def handle_get_logout(scope, recv, send):
    raise NotImplementedError


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
