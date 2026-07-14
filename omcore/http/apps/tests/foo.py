from ... import all as hu
from ... import asgi
from ..routes import HANDLES_APP_MARKER_PROCESSORS
from ..routes import Route
from ..routes import RouteHandlerApp
from ..routes import RouteHandlerHolder
from ..routes import build_route_handler_map
from ..routes import handles


##


class FooHandler(RouteHandlerHolder):
    @handles(Route.get('/'))
    async def handle_get_index(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_TEXT, body=b'hi!')

    @handles(Route.get('/foo'))
    async def handle_get_foo(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_TEXT, body=b'foo!')

    @handles(Route.post('/bar'))
    async def handle_post_bar(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_TEXT, body=b'bar!')


##


def build_foo_app() -> asgi.App:
    rhs = {FooHandler()}
    rhm = build_route_handler_map(rhs, {**HANDLES_APP_MARKER_PROCESSORS})
    rha = RouteHandlerApp(rhm)
    return rha
