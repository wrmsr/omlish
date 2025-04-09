from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles


class DiagHandler(RouteHandlerHolder):
    @handles(Route.post('/boom'))
    async def handle_post_boom(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        raise Exception('boom')
