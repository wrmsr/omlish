from omcore import lang
from omcore.http import asgi
from omcore.http.apps.base import url_for
from omcore.http.apps.markers import AppMarker
from omcore.http.apps.markers import AppMarkerProcessor
from omcore.http.apps.markers import append_app_marker
from omcore.http.apps.sessions import SESSION

from ...users import User
from .users import USER


##


def login_user(user: User, *, remember: bool = False) -> None:
    SESSION.get()['_user_id'] = user.id


#


@lang.decorator
async def _login_required(fn: asgi.App, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
    if USER.get() is None:
        await asgi.redirect_response(send, url_for('login'))
        return

    await fn(scope, recv, send)


#


class _LoginRequiredAppMarker(AppMarker, lang.Singleton, lang.Final):
    pass


def login_required(fn):
    append_app_marker(fn, _LoginRequiredAppMarker())
    return fn


class _LoginRequiredAppMarkerProcessor(AppMarkerProcessor):
    def process_app(self, app: asgi.App) -> asgi.App:
        return _login_required(app)  # noqa
