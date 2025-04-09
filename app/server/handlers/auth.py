import dataclasses as dc

from omlish.formats import json
from omlish.http import all as hu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import send_response
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles

from ...users import UserStore
from ..apps.users import get_auth_user


@dc.dataclass(frozen=True)
class AuthHandler(RouteHandlerHolder):
    _users: UserStore

    @handles(Route.post('/check-auth'))
    async def handle_post_check_auth(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        if (user := await get_auth_user(scope, self._users)) is None:
            await send_response(send, 401)
            return

        dct = {
            'user_id': user.id,
            'user_name': user.name,
        }
        resp_body = json.dumps(dct).encode() + b'\n'

        await send_response(send, 200, hu.consts.CONTENT_TYPE_JSON_UTF8, body=resp_body)
