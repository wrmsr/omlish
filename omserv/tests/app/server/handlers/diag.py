from omlish.http import asgi
from omlish.http.apps.routes import Route
from omlish.http.apps.routes import RouteHandlerHolder
from omlish.http.apps.routes import handles


##


class DiagHandler(RouteHandlerHolder):
    @handles(Route.post('/boom'))
    async def handle_post_boom(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        raise Exception('boom')
