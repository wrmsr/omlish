"""
TODO:
 - remember - just a second cookie lol
 - chrome save text boxes / login
 - with_session / with_user / login_required as *marks* not wrappers
  - maybe *both*, just to last-ditch validate login_required
 - logout is POST
 - template reload doesn't reload includes

https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""
import datetime

from omlish import inject as inj
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.secrets import all as sec
from omserv.apps.routes import RouteHandlerApp
from omserv.apps.templates import JinjaTemplates

from ..users import InMemoryUserStore
from ..users import UserStore
from ..usersdb import DbUserStore
from .apps import inject as apps_inj
from .handlers import inject as handlers_inj


##


def bind_in_memory_user_store() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(InMemoryUserStore, singleton=True),
        inj.bind(UserStore, to_key=InMemoryUserStore),
    )


def bind_db_user_store() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(DbUserStore, singleton=True),
        inj.bind(UserStore, to_key=DbUserStore),
    )


##


def _bind_cookie_session_store() -> inj.Elemental:
    return inj.private(
        inj.bind(sessions.Signer.Config(
            secret_key=sec.SecretRef('session_secret_key'),
        )),
        inj.bind(sessions.Signer, singleton=True),

        inj.bind(sessions.SessionMarshal, singleton=True),

        inj.bind(sessions.CookieSessionStore.Config(
            max_age=datetime.timedelta(days=31),
        )),
        inj.bind(sessions.CookieSessionStore, singleton=True, expose=True),
    )


def bind_app() -> inj.Elemental:
    return inj.private(
        inj.bind(JinjaTemplates.Config(
            resource_root=__package__ + '.templates',
            reload=True,
        )),

        apps_inj.bind(),

        handlers_inj.bind(),

        _bind_cookie_session_store(),

        inj.bind(RouteHandlerApp, singleton=True),
        inj.bind(AsgiApp, to_key=RouteHandlerApp, expose=True),
    )
