import contextvars
import dataclasses as dc
import datetime
import logging
import os
import typing as ta

from omlish import check
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


T = ta.TypeVar('T')


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
            obj = {
                **obj,
                'headers': [
                    *obj.get('headers', []),
                    *COOKIE_SESSION_STORE.build_headers(out_session),
                ],
            }

        await send(obj)

    in_session = COOKIE_SESSION_STORE.extract(scope)
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


def base_server_url() -> str:
    return os.environ.get('BASE_SERVER_URL', 'http://localhost:8000/')


@j2_helper
def url_for(s: str) -> str:
    return base_server_url() + s


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


def login_user(user: User, *, remember: bool = False) -> None:
    SESSION.get()['_user_id'] = user.id


#


class AppMarker(lang.Abstract):
    pass


APP_MARKERS_ATTR = '__app_markers__'


def append_app_marker(obj: ta.Any, marker: AppMarker) -> None:
    tgt = lang.unwrap_func(obj)
    tgt.__dict__.setdefault(APP_MARKERS_ATTR, []).append(marker)


def get_app_markers(obj) -> ta.Sequence[AppMarker]:
    tgt = lang.unwrap_func(obj)
    try:
        dct = tgt.__dict__
    except AttributeError:
        return ()
    return dct.get(APP_MARKERS_ATTR, ())


#


class _LoginRequiredAppMarker(AppMarker, lang.Singleton, lang.Final):
    pass


def login_required(fn):
    @lang.decorator
    async def inner(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        if USER.get() is None:
            await redirect_response(send, url_for('login'))
            return

        await fn(scope, recv, send)

    append_app_marker(fn, _LoginRequiredAppMarker())
    return inner(fn)


##


class Route(ta.NamedTuple):
    method: str
    path: str


class RouteHandler(ta.NamedTuple):
    route: Route
    handler: AsgiApp


@dc.dataclass(frozen=True)
class _HandlesAppMarker(AppMarker, lang.Final):
    routes: ta.Sequence[Route]


def handles(*routes: Route):
    def inner(fn):
        append_app_marker(fn, _HandlesAppMarker(routes))
        return fn

    routes = tuple(map(check.of_isinstance(Route), routes))
    return inner


##


class Handler_(lang.Abstract):  # noqa
    def get_route_handlers(self) -> ta.Iterable[RouteHandler]:
        return get_marked_route_handlers(self)


def get_marked_route_handlers(h: Handler_) -> ta.Sequence[RouteHandler]:
    ret: list[RouteHandler] = []

    cdct: dict[str, ta.Any] = {}
    for mcls in reversed(type(h).__mro__):
        cdct.update(**mcls.__dict__)

    for att, obj in cdct.items():
        if not (mks := get_app_markers(obj)):
            continue
        if not (hms := [m for m in mks if isinstance(m, _HandlesAppMarker)]):
            continue
        if not (rs := [r for hm in hms for r in hm.routes]):
            continue

        app = getattr(h, att)
        ret.extend(RouteHandler(r, app) for r in rs)

    return ret
