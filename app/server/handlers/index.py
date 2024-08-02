import dataclasses as dc
import typing as ta

from omlish import http as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import finish_response
from omlish.http.asgi import start_response
from omlish.http.sessions import Session

from ..apps.j2 import J2Templates
from ..apps.routes import Handler_
from ..apps.routes import Route
from ..apps.routes import handles
from ..apps.sessions import with_session
from ..apps.users import with_user


@dc.dataclass(frozen=True)
class IndexHandler(Handler_):
    _current_session: ta.Callable[[], Session]
    _templates: J2Templates

    @handles(Route('GET', '/'))
    @with_session
    @with_user
    async def handle_get_index(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        session = self._current_session()

        session['c'] = session.get('c', 0) + 1

        html = self._templates.render('index.html.j2')
        await start_response(send, 200, hu.consts.CONTENT_TYPE_HTML_UTF8)  # noqa
        await finish_response(send, html)
