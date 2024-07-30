"""
TODO:
 - remember - just a second cookie lol
 - chrome save text boxes / login

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import contextvars
import dataclasses as dc
import datetime
import functools
import importlib.resources
import logging
import os
import typing as ta

import anyio.to_thread

from omlish import asyncs as asu
from omlish import check
from omlish import http as hu
from omlish import json
from omlish import lang
from omlish import logs
from omlish.asyncs import anyio as anu
from omlish.http import sessions
from omlish.http.asgi import finish_response
from omlish.http.asgi import read_body
from omlish.http.asgi import read_form_body
from omlish.http.asgi import redirect_response
from omlish.http.asgi import send_response
from omlish.http.asgi import start_response
from omlish.http.asgi import stub_lifespan

from ...config import Config
from ...serving import serve
from .j2 import j2_helper
from .j2 import load_templates
from .j2 import render_template
from .passwords import check_password_hash
from .passwords import generate_password_hash
from .users import USERS
from .users import User


log = logging.getLogger(__name__)


##


SCOPE: contextvars.ContextVar[dict[str, ta.Any]] = contextvars.ContextVar('scope')


##


COOKIE_SESSION_STORE = sessions.CookieSessionStore(
    marshal=sessions.SessionMarshal(
        signer=sessions.Signer(sessions.Signer.Config(
            secret_key='secret-key-goes-here',  # noqa
        )),
    ),
    config=sessions.CookieSessionStore.Config(
        max_age=datetime.timedelta(days=31),
    ),
)


SESSION: contextvars.ContextVar[sessions.Session] = contextvars.ContextVar('session')


def with_session(fn):
    async def inner(scope, recv, send):
        async def _send(obj):
            if obj['type'] == 'http.response.start':
                out_session = SESSION.get()
                print('\n'.join([f'{scope=}', f'{in_session=}', f'{obj=}', f'{out_session=}', '']))
                obj = {
                    **obj,
                    'headers': [
                        *obj.get('headers', []),
                        *COOKIE_SESSION_STORE.build_headers(out_session),
                    ],
                }

            await send(obj)

        in_session = COOKIE_SESSION_STORE.extract(scope)
        print('\n'.join([f'{scope=}', f'{in_session=}', '']))
        with lang.context_var_setting(SESSION, in_session):
            await fn(scope, recv, _send)

    return inner


##


@j2_helper
def get_flashed_messages() -> list[str]:
    session = SESSION.get()
    try:
        ret = session['_flashes']
    except KeyError:
        return []
    del session['_flashes']
    return ret


def flash(msg: str) -> None:
    SESSION.get().setdefault('_flashes', []).append(msg)


#


BASE_SERVER_URL = os.environ.get('BASE_SERVER_URL', 'http://localhost:8000/')


@j2_helper
def url_for(s: str) -> str:
    return BASE_SERVER_URL + s


##


HANDLERS: dict[tuple[str, str], ta.Any] = {}


def handle(method: str, path: str):
    def inner(fn):
        HANDLERS[(method, path)] = fn
        return fn
    return inner


##


USER: contextvars.ContextVar[User | None] = contextvars.ContextVar('user', default=None)


@j2_helper
def current_user() -> User | None:
    return USER.get()


def with_user(fn):
    async def inner(scope, recv, send):
        session = SESSION.get()

        user_id = session.get('_user_id')
        if user_id is not None:
            user = USERS.get(id=user_id)
        else:
            user = None

        with lang.context_var_setting(USER, user):
            await fn(scope, recv, send)

    return inner


def login_required(fn):
    async def inner(scope, recv, send):
        if USER.get() is None:
            await redirect_response(send, url_for('login'))
            return

        await fn(scope, recv, send)

    return inner


def login_user(user: User, *, remember: bool = False) -> None:
    SESSION.get()['_user_id'] = user.id


##


@handle('GET', '/')
@with_session
@with_user
async def handle_get_index(scope, recv, send):
    session = SESSION.get()

    session['c'] = session.get('c', 0) + 1

    html = render_template('index.html')
    await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
    await finish_response(send, html)


#


@handle('GET', '/profile')
@with_session
@with_user
@login_required
async def handle_get_profile(scope, recv, send):
    user = check.not_none(USER.get())
    html = render_template(
        'profile.html',
        name=user.name,
        auth_token=user.auth_token or '',
    )
    await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
    await finish_response(send, html)


@handle('POST', '/profile')
@with_session
@with_user
async def handle_post_profile(scope, recv, send):
    user = check.not_none(USER.get())

    dct = await read_form_body(recv)

    auth_token = dct[b'auth-token'].decode()

    user = dc.replace(user, auth_token=auth_token or None)
    USERS.update(user)

    await redirect_response(send, url_for('profile'))


#


@handle('GET', '/login')
@with_session
@with_user
async def handle_get_login(scope, recv, send):
    html = render_template('login.html')
    await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
    await finish_response(send, html)


@handle('POST', '/login')
@with_session
@with_user
async def handle_post_login(scope, recv, send):
    dct = await read_form_body(recv)

    email = dct[b'email'].decode()
    password = dct[b'password'].decode()  # noqa
    remember = b'remember' in dct  # noqa

    user = USERS.get(email=email)  # noqa

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')

        await redirect_response(send, url_for('login'))
        return

    login_user(user, remember=remember)
    await redirect_response(send, url_for('profile'))


#


@handle('GET', '/signup')
@with_session
@with_user
async def handle_get_signup(scope, recv, send):
    html = render_template('signup.html')
    await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
    await finish_response(send, html)


@handle('POST', '/signup')
@with_session
@with_user
async def handle_post_signup(scope, recv, send):
    dct = await read_form_body(recv)

    email = dct[b'email'].decode()
    password = dct[b'password'].decode()
    name = dct[b'name'].decode()

    USERS.create(
        email=email,
        password=generate_password_hash(password, method='scrypt'),
        name=name,
    )

    await redirect_response(send, url_for('login'))


#


@handle('GET', '/logout')
@with_session
@with_user
@login_required
async def handle_get_logout(scope, recv, send):
    SESSION.get().pop('_user_id', None)
    await redirect_response(send, url_for(''))


##


@lang.cached_function
def _favicon_bytes() -> bytes:
    return importlib.resources.files(__package__).joinpath('../../resources/favicon.ico').read_bytes()


@handle('GET', '/favicon.ico')
async def handle_get_favicon_ico(scope, recv, send):
    await send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=_favicon_bytes())


##


if ta.TYPE_CHECKING:
    import tiktoken
else:
    tiktoken = lang.proxy_import('tiktoken')


def _gpt2_enc() -> 'tiktoken.Encoding':
    return tiktoken.get_encoding('gpt2')


gpt2_enc = anu.LazyFn(functools.partial(anyio.to_thread.run_sync, _gpt2_enc))


BASIC_AUTH_PREFIX = b'Bearer '


@handle('POST', '/tik')
async def handle_post_tik(scope, recv, send):
    hdrs = dict(scope['headers'])
    auth = hdrs.get(b'authorization')
    if not auth or not auth.startswith(BASIC_AUTH_PREFIX):
        await send_response(send, 401)
        return

    auth_token = auth[len(BASIC_AUTH_PREFIX):].decode()
    user: User | None = None
    for u in USERS.get_all():
        if u.auth_token and u.auth_token == auth_token:
            user = u
            break
    if not user:
        await send_response(send, 401)
        return

    enc = await gpt2_enc.get()

    req_body = await read_body(recv)
    toks = enc.encode(req_body.decode())
    dct = {
        'user_id': user.id,
        'user_name': user.name,
        'tokens': toks,
    }
    resp_body = json.dumps(dct).encode() + b'\n'

    await send_response(send, 200, hu.consts.CONTENT_TYPE_JSON_UTF8, body=resp_body)


##


async def auth_app(scope, recv, send):
    match scope_ty := scope['type']:
        case 'lifespan':
            await stub_lifespan(scope, recv, send)
            return

        case 'http':
            handler = HANDLERS.get((scope['method'], scope['raw_path'].decode()))

            if handler is not None:
                with lang.context_var_setting(SCOPE, scope):
                    await handler(scope, recv, send)

            else:
                await send_response(send, 404)

        case _:
            raise ValueError(f'Unhandled scope type: {scope_ty!r}')


##


def _main() -> None:
    logs.configure_standard_logging(logging.INFO)

    load_templates()

    @asu.with_adapter_loop(wait=True)
    async def _a_main():
        await serve(
            auth_app,
            Config(),
            handle_shutdown_signals=True,
        )

    anyio.run(_a_main)


if __name__ == '__main__':
    _main()
