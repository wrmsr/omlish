import dataclasses as dc
import typing as ta

from omlish.http import all as hu
from omlish.http import asgi
from omlish.http.sessions import Session
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.apps.sessions import with_session
from omserv.apps.templates import JinjaTemplates

from ..apps.users import with_user


##


@dc.dataclass(frozen=True)
class IndexHandler(RouteHandlerHolder):
    _current_session: ta.Callable[[], Session]
    _templates: JinjaTemplates

    @handles(Route.get('/'))
    @with_session
    @with_user
    async def handle_get_index(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        session = self._current_session()

        views = session['c'] = session.get('c', 0) + 1

        html = self._templates.render('index.html.j2', views=views)
        await asgi.start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await asgi.finish_response(send, html)
