import contextvars
import dataclasses as dc

from omlish import lang
from omlish.http import asgi
from omlish.http import sessions
from omlish.logs import all as logs

from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import append_app_marker


log = logs.get_module_logger(globals())


##


SESSION: contextvars.ContextVar[sessions.Session] = contextvars.ContextVar('session')


class _WithSessionAppMarker(AppMarker, lang.Singleton, lang.Final):
    pass


def with_session(fn):
    return append_app_marker(fn, _WithSessionAppMarker())


@dc.dataclass(frozen=True)
class _WithSessionAppMarkerProcessor(AppMarkerProcessor):
    _ss: sessions.CookieSessionStore

    async def _wrap(self, fn: asgi.App, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
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

    def process_app(self, app: asgi.App) -> asgi.App:
        return lang.decorator(self._wrap)(app)  # noqa
