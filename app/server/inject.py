import datetime
import logging
import os

from omlish import inject as inj
from omlish import secrets as sec
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omserv.apps.base import BaseServerUrl
from omserv.apps.routes import RouteHandlerApp
from omserv.apps.templates import J2Templates

from ..users import InMemoryUserStore
from ..users import UserStore
from ..usersdb import DbUserStore
from .apps import inject as apps_inj
from .handlers import inject as handlers_inj


log = logging.getLogger(__name__)


##


def _bind_cookie_session_store() -> inj.Elemental:
    return inj.private(
        inj.bind(sessions.Signer.Config(
            secret_key=sec.Secret('session_secret_key'),
        )),
        inj.bind(sessions.Signer, singleton=True),

        inj.bind(sessions.SessionMarshal, singleton=True),

        inj.bind(sessions.CookieSessionStore.Config(
            max_age=datetime.timedelta(days=31),
        )),
        inj.bind(sessions.CookieSessionStore, singleton=True, expose=True),
    )


def _bind_in_memory_user_store() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(InMemoryUserStore, singleton=True),
        inj.bind(UserStore, to_key=InMemoryUserStore),
    )


def _bind_db_user_store() -> inj.Elemental:
    from ..dbs import bind_dbs

    return inj.as_elements(
        bind_dbs(),

        inj.bind(DbUserStore, singleton=True),
        inj.bind(UserStore, to_key=DbUserStore),
    )


def base_server_url() -> BaseServerUrl:
    return BaseServerUrl(os.environ.get('BASE_SERVER_URL', 'http://localhost:8000/'))


def bind() -> inj.Elemental:
    return inj.private(
        inj.bind(sec.Secrets, to_const=sec.SimpleSecrets({
            'session_secret_key': 'secret-key-goes-here',  # noqa
        })),

        inj.bind(J2Templates.Config(
            resource_root=__package__ + '.templates',
            reload=True,
        )),

        inj.bind(base_server_url, singleton=True),

        apps_inj.bind(),

        handlers_inj.bind(),

        _bind_in_memory_user_store(),
        # _bind_db_user_store(),

        _bind_cookie_session_store(),

        inj.bind(RouteHandlerApp, singleton=True),
        inj.bind(AsgiApp, to_key=RouteHandlerApp, expose=True),
    )
