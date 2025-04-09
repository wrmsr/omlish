from omlish.http import all as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.server.resources import favicon_bytes


class FaviconHandler(RouteHandlerHolder):
    @handles(Route.get('/favicon.ico'))
    async def handle_get_favicon_ico(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=favicon_bytes())
