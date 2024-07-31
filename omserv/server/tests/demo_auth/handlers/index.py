import typing as ta

from omlish import http as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import start_response

from ..base import SESSION
from ..base import Handler_
from ..base import Route
from ..base import RouteHandler
from ..base import with_session
from ..base import with_user
from ..j2 import J2Templates


class IndexHandler(Handler_):
    def __init__(
            self,
            templates: J2Templates,
    ) -> None:
        super().__init__()
        self._templates = templates

    def get_route_handlers(self) -> ta.Iterable[RouteHandler]:
        return [
            RouteHandler(Route('GET', '/'), self.handle_get_index),  # noqa
        ]

    @with_session
    @with_user
    async def handle_get_index(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        session = SESSION.get()

        session['c'] = session.get('c', 0) + 1

        html = self._templates.render('index.html.j2')
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)
