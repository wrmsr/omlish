import dataclasses as dc

from omlish.formats import json
from omlish.http import all as hu
from omlish.http import asgi
from omserv.apps.routes import Route
from omserv.apps.routes import RouteHandlerHolder
from omserv.apps.routes import handles

from ...users import UserStore
from ..apps.users import get_auth_user


@dc.dataclass(frozen=True)
class AuthHandler(RouteHandlerHolder):
    _users: UserStore

    @handles(Route.post('/check-auth'))
    async def handle_post_check_auth(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        if (user := await get_auth_user(scope, self._users)) is None:
            await asgi.send_response(send, 401)
            return

        dct = {
            'user_id': user.id,
            'user_name': user.name,
        }
        resp_body = json.dumps(dct).encode() + b'\n'

        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_JSON_UTF8, body=resp_body)
