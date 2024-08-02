import contextvars
import dataclasses as dc
import logging
import typing as ta

from omlish import lang
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend

from .j2 import j2_helper
from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import append_app_marker


T = ta.TypeVar('T')


log = logging.getLogger(__name__)


##


SESSION: contextvars.ContextVar[sessions.Session] = contextvars.ContextVar('session')


class _WithSessionAppMarker(AppMarker, lang.Singleton, lang.Final):
    pass


def with_session(fn):
    return append_app_marker(fn, _WithSessionAppMarker())


@dc.dataclass(frozen=True)
class _WithSessionAppMarkerProcessor(AppMarkerProcessor):
    _ss: sessions.CookieSessionStore

    def __call__(self, app: AsgiApp) -> AsgiApp:
        @lang.decorator
        async def _with_session(fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
            async def _send(obj):
                if obj['type'] == 'http.response.start':
                    out_session = SESSION.get()
                    obj = {
                        **obj,
                        'headers': [
                            *obj.get('headers', []),
                            *self._ss.build_headers(out_session),
                        ],
                    }

                await send(obj)

            in_session = self._ss.extract(scope)
            with lang.context_var_setting(SESSION, in_session):
                await fn(scope, recv, _send)

        return _with_session(app)  # noqa


##


@j2_helper
def get_flashed_messages() -> list[str]:
    session = SESSION.get()
    try:
        ret = session['_flashes']
    except KeyError:
        return []
    del session['_flashes']
    return ret


def flash(msg: str) -> None:
    SESSION.get().setdefault('_flashes', []).append(msg)
