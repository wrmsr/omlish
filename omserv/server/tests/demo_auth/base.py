import abc
import contextvars
import datetime
import logging
import os
import typing as ta

from omlish import lang
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import redirect_response

from .j2 import j2_helper
from .users import User
from .users import UserStore


log = logging.getLogger(__name__)


##


SCOPE: contextvars.ContextVar[AsgiScope] = contextvars.ContextVar('scope')


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


@lang.decorator
async def with_session(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
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


USER_STORE = UserStore()

USER: contextvars.ContextVar[User | None] = contextvars.ContextVar('user', default=None)


@j2_helper
def current_user() -> User | None:
    return USER.get()


@lang.decorator
async def with_user(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    session = SESSION.get()

    user_id = session.get('_user_id')
    if user_id is not None:
        user = USER_STORE.get(id=user_id)
    else:
        user = None

    with lang.context_var_setting(USER, user):
        await fn(scope, recv, send)


@lang.decorator
async def login_required(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    if USER.get() is None:
        await redirect_response(send, url_for('login'))
        return

    await fn(scope, recv, send)


def login_user(user: User, *, remember: bool = False) -> None:
    SESSION.get()['_user_id'] = user.id


##


class Route(ta.NamedTuple):
    method: str
    path: str


class RouteHandler(ta.NamedTuple):
    route: Route
    handler: AsgiApp


##


class Handler_(lang.Abstract):  # noqa
    @abc.abstractmethod
    def get_route_handlers(self) -> ta.Iterable[RouteHandler]:
        raise NotImplementedError
