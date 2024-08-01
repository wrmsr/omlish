import importlib.resources

from omlish import http as hu
from omlish import lang
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response

from ..base import Handler_
from ..base import Route
from ..base import handles


@lang.cached_function
def _favicon_bytes() -> bytes:
    return importlib.resources.files(__package__).joinpath('../../../resources/favicon.ico').read_bytes()


class FaviconHandler(Handler_):
    @handles(Route('GET', '/favicon.ico'))
    async def handle_get_favicon_ico(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        await send_response(send, 200, hu.consts.CONTENT_TYPE_ICON, body=_favicon_bytes())
