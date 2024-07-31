"""
TODO:
 - remember - just a second cookie lol
 - chrome save text boxes / login
 - with_session / with_user / login_required as *marks* not wrappers
  - maybe *both*, just to last-ditch validate login_required
 - logout is POST

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import logging
import typing as ta

import anyio.to_thread

from omlish import asyncs as asu
from omlish import lang
from omlish import logs
from omlish.http.asgi import AsgiApp_
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response
from omlish.http.asgi import stub_lifespan

from ...config import Config
from ...serving import serve
from .base import SCOPE
from .base import SESSION
from .base import USER
from .base import USER_STORE
from .base import Handler_
from .base import Route
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


@lang.cached_function
def _auth_app() -> AuthApp:
    templates = J2Templates(J2Templates.Config(
        reload=True,
    ))

    current_scope = lang.Func0(SCOPE.get)  # noqa
    current_session = lang.Func0(SESSION.get)
    current_user = lang.Func0(USER.get)

    handlers: list[Handler_] = [
        IndexHandler(current_session=current_session, templates=templates),
        ProfileHandler(current_user=current_user, templates=templates, users=USER_STORE),
        LoginHandler(templates=templates, users=USER_STORE),
        SignupHandler(templates=templates, users=USER_STORE),
        LogoutHandler(),
        FaviconHandler(),
        TikHandler(users=USER_STORE),
    ]

    route_handlers: dict[Route, ta.Any] = {}
    for h in handlers:
        for rh in h.get_route_handlers():
            app = lang.unwrap_method(lang.unwrap_func(rh.handler))  # noqa
            route_handlers[rh.route] = rh.handler

    return AuthApp(
        route_handlers=route_handlers,
    )


async def auth_app(scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    await _auth_app()(scope, recv, send)


##


@asu.with_adapter_loop(wait=True)
async def _a_main() -> None:
    logs.configure_standard_logging(logging.INFO)

    await serve(
        auth_app,  # type: ignore
        Config(),
        handle_shutdown_signals=True,
    )


if __name__ == '__main__':
    anyio.run(_a_main)
