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
from omlish.http.asgi import AsgiApp_
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response
from omlish.http.asgi import stub_lifespan
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


class AuthApp(AsgiApp_):
    def __init__(
            self,
            *,
            route_handlers: dict[Route, ta.Any],
    ) -> None:
        super().__init__()

        self._route_handlers = route_handlers

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
        inj.as_(ta.Callable[[], AsgiScope], inj.const(SCOPE.get)),
        inj.as_(ta.Callable[[], Session], inj.const(SESSION.get)),
        inj.as_(ta.Callable[[], User | None], inj.const(USER.get)),

        inj.as_binding(inj.const(J2Templates.Config(reload=True))),
        inj.as_binding(inj.singleton(J2Templates)),

        inj.as_binding(inj.const(USER_STORE)),

        inj.bind_set_provider(ta.AbstractSet[Handler_]),

        *itertools.chain.from_iterable([
            inj.singleton(hc),
            inj.SetBinding(inj.as_key(ta.AbstractSet[Handler_]), inj.Key(hc)),
        ] for hc in [
            IndexHandler,
            ProfileHandler,
            LoginHandler,
            SignupHandler,
            LogoutHandler,
            FaviconHandler,
            TikHandler,
        ]),

        inj.as_binding(inj.singleton(_build_route_handler_map)),

        inj.as_binding(inj.singleton(RouteHandlerApp)),
    ))

    return i[RouteHandlerApp]


async def server_app(scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    await _server_app()(scope, recv, send)
