import dataclasses as dc
import functools
import typing as ta

import anyio.to_thread

from omlish import http as hu
from omlish import lang
from omlish.asyncs import anyio as anu
from omlish.http.asgi import AsgiRecv
from omlish.http.asgi import AsgiScope
from omlish.http.asgi import AsgiSend
from omlish.http.asgi import read_body
from omlish.http.asgi import send_response
from omlish.serde import json
from omserv.apps.routes import Handler_
from omserv.apps.routes import Route
from omserv.apps.routes import handles

from ...users import User
from ...users import UserStore


if ta.TYPE_CHECKING:
    import tiktoken
else:
    tiktoken = lang.proxy_import('tiktoken')


def _gpt2_enc() -> 'tiktoken.Encoding':
    return tiktoken.get_encoding('gpt2')


gpt2_enc = anu.LazyFn(functools.partial(anyio.to_thread.run_sync, _gpt2_enc))


@dc.dataclass(frozen=True)
class TikHandler(Handler_):
    _users: UserStore

    @handles(Route.post('/tik'))
    async def handle_post_tik(self, scope: AsgiScope, recv: AsgiRecv, send: AsgiSend) -> None:
        hdrs = dict(scope['headers'])
        auth = hdrs.get(hu.consts.HEADER_AUTH.lower())
        if not auth or not auth.startswith(hu.consts.BEARER_AUTH_HEADER_PREFIX):
            await send_response(send, 401)
            return

        auth_token = auth[len(hu.consts.BEARER_AUTH_HEADER_PREFIX):].decode()
        user: User | None = None
        for u in await self._users.get_all():
            if u.auth_token and u.auth_token == auth_token:
                user = u
                break
        if not user:
            await send_response(send, 401)
            return

        enc = await gpt2_enc.get()

        req_body = await read_body(recv)
        toks = enc.encode(req_body.decode())
        dct = {
            'user_id': user.id,
            'user_name': user.name,
            'tokens': toks,
        }
        resp_body = json.dumps(dct).encode() + b'\n'

        await send_response(send, 200, hu.consts.CONTENT_TYPE_JSON_UTF8, body=resp_body)
