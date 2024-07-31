import importlib.resources
import typing as ta

from omlish import http as hu
from omlish import lang
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response

from ..base import Handler_
from ..base import Route
from ..base import RouteHandler


@lang.cached_function
def _favicon_bytes(self) -> bytes:
    return importlib.resources.files(__package__).joinpath('../../../resources/favicon.ico').read_bytes()


class FaviconHandler(Handler_):

    def get_route_handlers(self) -> ta.Iterable[RouteHandler]:
        return [
            RouteHandler(Route('GET', '/favicon.ico'), self.handle_get_favicon_ico),  # noqa
        ]

    async def handle_get_favicon_ico(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=_favicon_bytes())
