import contextvars
import dataclasses as dc
import logging

from omlish import lang
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omserv.apps.markers import AppMarker
from omserv.apps.markers import AppMarkerProcessor
from omserv.apps.markers import append_app_marker
from omserv.apps.sessions import SESSION
from omserv.apps.templates import j2_helper

from ...users import User
from ...users import UserStore


log = logging.getLogger(__name__)


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
                user = await self._users.get(id=user_id)
            else:
                user = None

            with lang.context_var_setting(USER, user):
                await fn(scope, recv, send)

        return _with_user(app)  # noqa
