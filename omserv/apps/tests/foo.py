from omlish.http import all as hu
from omlish.http import asgi

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


##


async def _a_main() -> None:
    import functools

    import anyio

    from omlish.sockets.ports import get_available_port

    from ...server.config import Config
    from ...server.default import serve
    from ...server.types import AsgiWrapper

    app = build_foo_app()

    port = get_available_port()
    server_bind = f'127.0.0.1:{port}'
    base_url = f'http://{server_bind}/'

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            serve,
            AsgiWrapper(app),  # noqa
            Config(
                bind=(server_bind,),
            ),
        ))

        print(f'Serving at {base_url}')


if __name__ == '__main__':
    import anyio

    anyio.run(_a_main)
