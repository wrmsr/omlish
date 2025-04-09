from omlish.http import all as hu
from omlish.http import asgi
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles
from omserv.server.resources import favicon_bytes


class FaviconHandler(RouteHandlerHolder):
    @handles(Route.get('/favicon.ico'))
    async def handle_get_favicon_ico(self, scope: asgi.AsgiScope, recv: asgi.AsgiRecv, send: asgi.AsgiSend) -> None:
        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=favicon_bytes())
