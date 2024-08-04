import contextvars
import dataclasses as dc
import logging

from omlish import lang
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend

from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import append_app_marker


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

    async def _wrap(self, fn: AsgiApp, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
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

    def __call__(self, app: AsgiApp) -> AsgiApp:
        return lang.decorator(self._wrap)(app)  # noqa
