from omlish.http import all as hu
from omlish.http import asgi
from omlish.http.apps.routes import Route
from omlish.http.apps.routes import RouteHandlerHolder
from omlish.http.apps.routes import handles

from .....server.resources import favicon_bytes


##


class FaviconHandler(RouteHandlerHolder):
    @handles(Route.get('/favicon.ico'))
    async def handle_get_favicon_ico(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=favicon_bytes())
