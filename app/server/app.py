"""
TODO:
 - remember - just a second cookie lol
 - chrome save text boxes / login
 - with_session / with_user / login_required as *marks* not wrappers
  - maybe *both*, just to last-ditch validate login_required
 - logout is POST

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import itertools
import logging
import typing as ta

from omlish import inject as inj
from omlish import lang
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.sessions import Session

from .base import SCOPE
from .base import SESSION
from .base import USER
from .base import USER_STORE
from .base import Handler_
from .base import Route
from .base import RouteHandlerApp
from .base import User
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


def _build_route_handler_map(handlers: ta.AbstractSet[Handler_]) -> ta.Mapping[Route, AsgiApp]:
    route_handlers: dict[Route, AsgiApp] = {}
    for h in handlers:
        for rh in h.get_route_handlers():
            markers = get_app_markers(rh.handler)  # noqa
            route_handlers[rh.route] = rh.handler
    return route_handlers


@lang.cached_function
def _server_app() -> AsgiApp:
    i = inj.create_injector(inj.as_elements(
        inj.bind(ta.Callable[[], AsgiScope], to_const=SCOPE.get),
        inj.bind(ta.Callable[[], Session], to_const=SESSION.get),
        inj.bind(ta.Callable[[], User | None], to_const=USER.get),

        inj.bind(J2Templates.Config(reload=True)),
        inj.bind(J2Templates, singleton=True),

        inj.bind(USER_STORE),

        inj.set_binder[Handler_](),

        *itertools.chain.from_iterable([
            inj.bind(hc, singleton=True),
            inj.set_binder[Handler_]().bind(hc),
        ] for hc in [
            IndexHandler,
            ProfileHandler,
            LoginHandler,
            SignupHandler,
            LogoutHandler,
            FaviconHandler,
            TikHandler,
        ]),

        inj.bind(_build_route_handler_map, singleton=True),

        inj.bind(RouteHandlerApp, singleton=True),
    ))

    return i[RouteHandlerApp]


async def server_app(scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    await _server_app()(scope, recv, send)
