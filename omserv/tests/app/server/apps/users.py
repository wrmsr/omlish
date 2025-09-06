import contextvars
import dataclasses as dc

from omlish import lang
from omlish.http import all as hu
from omlish.http import asgi
from omlish.logs import all as logs

from .....apps.markers import AppMarker
from .....apps.markers import AppMarkerProcessor
from .....apps.markers import append_app_marker
from .....apps.sessions import SESSION
from .....apps.templates import jinja_helper
from ...users import User
from ...users import UserStore


log = logs.get_module_logger(globals())


##


USER: contextvars.ContextVar[User | None] = contextvars.ContextVar('user', default=None)


@jinja_helper
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

    async def _wrap(self, fn: asgi.App, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        session = SESSION.get()

        user_id = session.get('_user_id')
        if user_id is not None:
            user = await self._users.get(id=user_id)
        else:
            user = None

        with lang.context_var_setting(USER, user):
            await fn(scope, recv, send)

    def process_app(self, app: asgi.App) -> asgi.App:
        return lang.decorator(self._wrap)(app)  # noqa


##


async def get_auth_user(scope: asgi.Scope, users: UserStore) -> User | None:
    hdrs = dict(scope['headers'])
    auth = hdrs.get(hu.consts.HEADER_AUTH.lower())
    if not auth or not auth.startswith(hu.consts.BEARER_AUTH_HEADER_PREFIX):
        return None

    auth_token = auth[len(hu.consts.BEARER_AUTH_HEADER_PREFIX):].decode()
    for u in await users.get_all():
        if u.auth_token and u.auth_token == auth_token:
            return u

    return None
