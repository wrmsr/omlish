import abc
import contextvars
import dataclasses as dc
import logging
import os
import typing as ta

from omlish import check
from omlish import lang
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiApp_
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import redirect_response
from omlish.http.asgi import send_response
from omlish.http.asgi import stub_lifespan

from .j2 import j2_helper
from .users import User
from .users import UserStore


T = ta.TypeVar('T')


log = logging.getLogger(__name__)


##


SCOPE: contextvars.ContextVar[AsgiScope] = contextvars.ContextVar('scope')


##


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


class AppMarkerProcessor(lang.Abstract):
    @abc.abstractmethod
    def __call__(self, app: AsgiApp) -> AsgiApp:
        return app


APP_MARKER_PROCESSORS: dict[type[AppMarker], type[AppMarkerProcessor]] = {}


class NopAppMarkerProcessor(AppMarkerProcessor):
    def __call__(self, app: AsgiApp) -> AsgiApp:
        return app


##


SESSION: contextvars.ContextVar[sessions.Session] = contextvars.ContextVar('session')


#


class _WithSessionAppMarker(AppMarker, lang.Singleton, lang.Final):
    pass


def with_session(fn):
    append_app_marker(fn, _WithSessionAppMarker())
    return fn


@dc.dataclass(frozen=True)
class _WithSessionAppMarkerProcessor(AppMarkerProcessor):
    _ss: sessions.CookieSessionStore

    def __call__(self, app: AsgiApp) -> AsgiApp:
        @lang.decorator
        async def _with_session(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
            async def _send(obj):
                if obj['type'] == 'http.response.start':
                    out_session = SESSION.get()
                    obj = {
                        **obj,
                        'headers': [
                            *obj.get('headers', []),
                            *self._ss.build_headers(out_session),
                        ],
                    }

                await send(obj)

            in_session = self._ss.extract(scope)
            with lang.context_var_setting(SESSION, in_session):
                await fn(scope, recv, _send)

        return _with_session(app)  # noqa


APP_MARKER_PROCESSORS[_WithSessionAppMarker] = _WithSessionAppMarkerProcessor


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


USER: contextvars.ContextVar[User | None] = contextvars.ContextVar('user', default=None)


@j2_helper
def current_user() -> User | None:
    return USER.get()


#


class _WithUserAppMarker(AppMarker, lang.Singleton, lang.Final):
    pass


def with_user(fn):
    append_app_marker(fn, _WithUserAppMarker())
    return fn


@dc.dataclass(frozen=True)
class _WithUserAppMarkerProcessor(AppMarkerProcessor):
    _users: UserStore

    def __call__(self, app: AsgiApp) -> AsgiApp:
        @lang.decorator
        async def _with_user(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
            session = SESSION.get()

            user_id = session.get('_user_id')
            if user_id is not None:
                user = self._users.get(id=user_id)
            else:
                user = None

            with lang.context_var_setting(USER, user):
                await fn(scope, recv, send)

        return _with_user(app)  # noqa


APP_MARKER_PROCESSORS[_WithUserAppMarker] = _WithUserAppMarkerProcessor


#


def login_user(user: User, *, remember: bool = False) -> None:
    SESSION.get()['_user_id'] = user.id


#


@lang.decorator
async def _login_required(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    if USER.get() is None:
        await redirect_response(send, url_for('login'))
        return

    await fn(scope, recv, send)


#


class _LoginRequiredAppMarker(AppMarker, lang.Singleton, lang.Final):
    pass


def login_required(fn):
    append_app_marker(fn, _LoginRequiredAppMarker())
    return fn


class _LoginRequiredAppMarkerProcessor(AppMarkerProcessor):
    def __call__(self, app: AsgiApp) -> AsgiApp:
        return _login_required(app)  # noqa


APP_MARKER_PROCESSORS[_LoginRequiredAppMarker] = _LoginRequiredAppMarkerProcessor


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


APP_MARKER_PROCESSORS[_HandlesAppMarker] = NopAppMarkerProcessor


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


##


@dc.dataclass(frozen=True)
class RouteHandlerApp(AsgiApp_):
    _route_handlers: ta.Mapping[Route, AsgiApp]

    async def __call__(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        match scope_ty := scope['type']:
            case 'lifespan':
                await stub_lifespan(scope, recv, send)
                return

            case 'http':
                route = Route(scope['method'], scope['raw_path'].decode())
                handler = self._route_handlers.get(route)

                if handler is not None:
                    with lang.context_var_setting(SCOPE, scope):
                        await handler(scope, recv, send)

                else:
                    await send_response(send, 404)

            case _:
                raise ValueError(f'Unhandled scope type: {scope_ty!r}')
