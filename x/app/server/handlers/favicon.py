from omcore.http import all as hu
from omcore.http import asgi
from omcore.http.apps.routes import Route
from omcore.http.apps.routes import RouteHandlerHolder
from omcore.http.apps.routes import handles
from omcore.http.resources import favicon_bytes


##


class FaviconHandler(RouteHandlerHolder):
    @handles(Route.get('/favicon.ico'))
    async def handle_get_favicon_ico(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=favicon_bytes())
