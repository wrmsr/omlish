"""
TODO:
 - remember - just a second cookie lol
 - chrome save text boxes / login
 - with_session / with_user / login_required as *marks* not wrappers
  - maybe *both*, just to last-ditch validate login_required
 - logout is POST

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import datetime
import logging
import typing as ta

from omlish import inject as inj
from omlish import lang
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend

from .base import APP_MARKER_PROCESSORS
from .base import SCOPE
from .base import SESSION
from .base import USER
from .base import Handler_
from .base import Route
from .base import RouteHandlerApp
from .base import User
from .base import UserStore
from .base import get_app_markers
from .handlers.favicon import FaviconHandler
from .handlers.index import IndexHandler
from .handlers.login import LoginHandler
from .handlers.logout import LogoutHandler
from .handlers.profile import ProfileHandler
from .handlers.signup import SignupHandler
from .handlers.tik import TikHandler
from .j2 import J2Templates


log = logging.getLogger(__name__)


##


def _build_route_handler_map(
        i: inj.Injector,
        handlers: ta.AbstractSet[Handler_],
) -> ta.Mapping[Route, AsgiApp]:
    route_handlers: dict[Route, AsgiApp] = {}
    for h in handlers:
        for rh in h.get_route_handlers():
            app = rh.handler
            markers = get_app_markers(rh.handler)
            for m in markers:
                mp = APP_MARKER_PROCESSORS[type(m)]
                if mp is not None:
                    app = i.inject(mp)(app)
            route_handlers[rh.route] = app
    return route_handlers


def bind_handler(hc: type[Handler_]) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(hc, singleton=True),
        inj.set_binder[Handler_]().bind(hc),
    )


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


def bind_server_app() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(ta.Callable[[], AsgiScope], to_const=SCOPE.get),
        inj.bind(ta.Callable[[], sessions.Session], to_const=SESSION.get),
        inj.bind(ta.Callable[[], User | None], to_const=USER.get),

        inj.bind(J2Templates.Config(reload=True)),
        inj.bind(J2Templates, singleton=True),

        inj.bind(sessions.CookieSessionStore, to_const=COOKIE_SESSION_STORE),

        inj.bind(UserStore, singleton=True),

        inj.set_binder[Handler_](),

        bind_handler(IndexHandler),
        bind_handler(ProfileHandler),
        bind_handler(LoginHandler),
        bind_handler(SignupHandler),
        bind_handler(LogoutHandler),
        bind_handler(FaviconHandler),
        bind_handler(TikHandler),

        inj.bind(_build_route_handler_map, singleton=True),

        inj.bind(RouteHandlerApp, singleton=True),
        inj.bind(AsgiApp, to_key=RouteHandlerApp),
    )


@lang.cached_function
def _server_app() -> AsgiApp:
    return inj.create_injector(bind_server_app()).provide(AsgiApp)


async def server_app(scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    await _server_app()(scope, recv, send)
