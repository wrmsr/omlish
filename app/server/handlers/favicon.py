from omlish import http as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response
from omserv.server.resources import favicon_bytes

from ..apps.routes import Handler_
from ..apps.routes import Route
from ..apps.routes import handles


class FaviconHandler(Handler_):
    @handles(Route('GET', '/favicon.ico'))
    async def handle_get_favicon_ico(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=favicon_bytes())
