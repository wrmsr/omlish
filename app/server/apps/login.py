from omlish import lang
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import redirect_response

from ...users import User
from .base import url_for
from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import append_app_marker
from .sessions import SESSION
from .users import USER


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


