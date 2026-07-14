from omcore.http import asgi
from omcore.http.apps.routes import Route
from omcore.http.apps.routes import RouteHandlerHolder
from omcore.http.apps.routes import handles


##


class DiagHandler(RouteHandlerHolder):
    @handles(Route.post('/boom'))
    async def handle_post_boom(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        raise Exception('boom')
