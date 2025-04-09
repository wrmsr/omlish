import dataclasses as dc
import typing as ta

from omlish.http import all as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import start_response
from omlish.http.sessions import Session
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.apps.sessions import with_session
from omserv.apps.templates import JinjaTemplates

from ..apps.users import with_user


@dc.dataclass(frozen=True)
class IndexHandler(RouteHandlerHolder):
    _current_session: ta.Callable[[], Session]
    _templates: JinjaTemplates

    @handles(Route.get('/'))
    @with_session
    @with_user
    async def handle_get_index(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        session = self._current_session()

        views = session['c'] = session.get('c', 0) + 1

        html = self._templates.render('index.html.j2', views=views)
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)
