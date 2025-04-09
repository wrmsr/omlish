from omlish.http import asgi
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles


class DiagHandler(RouteHandlerHolder):
    @handles(Route.post('/boom'))
    async def handle_post_boom(self, scope: asgi.AsgiScope, recv: asgi.AsgiRecv, send: asgi.AsgiSend) -> None:
        raise Exception('boom')
