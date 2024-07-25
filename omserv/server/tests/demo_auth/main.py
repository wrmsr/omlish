"""
https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import dataclasses as dc
import importlib.resources
import itertools
import logging
import typing as ta
import urllib.parse

import anyio
import jinja2

from omlish import check
from omlish import lang
from omlish import logs
from omlish.http import consts

from ...config import Config
from ...serving import serve
from .utils import finish_response
from .utils import start_response
from .utils import stub_lifespan


log = logging.getLogger(__name__)


##


class _J2Loader(jinja2.BaseLoader):

    def get_source(self, environment, template):
        raise TypeError

    def list_templates(self):
        raise TypeError

    def load(self, environment, name, globals=None):
        return load_templates()[f'{name}.j2']


J2_ENV = jinja2.Environment(
    loader=_J2Loader(),
    autoescape=True,
)


@lang.cached_function
def load_templates() -> ta.Mapping[str, jinja2.Template]:
    ret: dict[str, jinja2.Template] = {}
    for fn in importlib.resources.files(__package__).joinpath('templates').iterdir():
        ret[fn.name] = J2_ENV.from_string(fn.read_text())
    return ret


class _EnvUser:
    is_authenticated = False


J2_DEFAULT_KWARGS = dict(
    get_flashed_messages=lambda: [],
    current_user=_EnvUser(),
)


def j2_helper(fn):
    J2_DEFAULT_KWARGS[fn.__name__] = fn
    return fn


def render_template(name: str, **kwargs: ta.Any) -> bytes:
    return load_templates()[f'{name}.j2'].render(**{**J2_DEFAULT_KWARGS, **kwargs}).encode()


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


@dc.dataclass(frozen=True)
class User:
    id: int
    email: str
    password: str
    name: str


class Users:
    def __init__(self) -> None:
        super().__init__()
        self._next_user_id = itertools.count()
        self._users_by_id: dict[int, User] = {}
        self._user_ids_by_email: dict[str, int] = {}

    def create(
            self,
            email: str,
            name: str,
    ) -> User:
        check.not_in(email, self._user_ids_by_email)
        u = User(
            id=next(self._next_user_id),
            email=email,
            name=name,
        )
        self._users_by_id[u.id] = u
        self._user_ids_by_email[u.email] = u.id
        return u

    def update(self, u: User) -> None:
        e = self._users_by_id[u.id]
        check.equal(u.email, e.email)
        self._users_by_id[u.id] = u


USERS = Users()


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
    name = check.single(dct[b'name']).decode()
    password = check.single(dct[b'password']).decode()

    raise NotImplementedError


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
