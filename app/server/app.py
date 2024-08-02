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

from omlish import inject as inj
from omlish import lang
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omserv.apps.j2 import J2Templates
from omserv.apps.routes import RouteHandlerApp

from ..users import UserStore
from .apps import inject as apps_inj
from .handlers import inject as handlers_inj


log = logging.getLogger(__name__)


##


def bind_cookie_session_store() -> inj.Elemental:
    return inj.private(
        inj.bind(sessions.Signer.Config(
            secret_key='secret-key-goes-here',  # noqa
        )),
        inj.bind(sessions.Signer, singleton=True),

        inj.bind(sessions.SessionMarshal, singleton=True),

        inj.bind(sessions.CookieSessionStore.Config(
            max_age=datetime.timedelta(days=31),
        )),
        inj.bind(sessions.CookieSessionStore, singleton=True, expose=True),
    )


def bind_server_app() -> inj.Elemental:
    return inj.private(
        inj.bind(J2Templates.Config(
            resource_root=__package__ + '.templates',
            reload=True,
        )),
        inj.bind(J2Templates, singleton=True),

        apps_inj.bind(),

        handlers_inj.bind(),

        bind_cookie_session_store(),

        inj.bind(UserStore, singleton=True),

        inj.bind(RouteHandlerApp, singleton=True),
        inj.bind(AsgiApp, to_key=RouteHandlerApp, expose=True),
    )


@lang.cached_function
def _server_app() -> AsgiApp:
    return inj.create_injector(bind_server_app()).provide(AsgiApp)


async def server_app(scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
    await _server_app()(scope, recv, send)
