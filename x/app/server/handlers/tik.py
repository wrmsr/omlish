import dataclasses as dc
import functools
import typing as ta

import anyio.to_thread

from omcore import lang
from omcore.asyncs import anyio as anu
from omcore.formats.json import all as json
from omcore.http import all as hu
from omcore.http import asgi
from omcore.http.apps.routes import Route
from omcore.http.apps.routes import RouteHandlerHolder
from omcore.http.apps.routes import handles

from ...users import UserStore
from ..apps.users import get_auth_user


if ta.TYPE_CHECKING:
    import tiktoken
else:
    tiktoken = lang.proxy_import('tiktoken')


##


def _gpt2_enc() -> 'tiktoken.Encoding':
    return tiktoken.get_encoding('gpt2')


gpt2_enc = anu.LazyFn(functools.partial(anyio.to_thread.run_sync, _gpt2_enc))


##


@dc.dataclass(frozen=True)
class TikHandler(RouteHandlerHolder):
    _users: UserStore

    @handles(Route.post('/tik'))
    async def handle_post_tik(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        if (user := await get_auth_user(scope, self._users)) is None:
            await asgi.send_response(send, 401)
            return

        enc = await gpt2_enc.get()

        req_body = await asgi.read_body(recv)
        toks = enc.encode(req_body.decode())
        dct = {
            'user_id': user.id,
            'user_name': user.name,
            'tokens': toks,
        }
        resp_body = json.dumps(dct).encode() + b'\n'

        await asgi.send_response(send, 200, hu.consts.CONTENT_TYPE_JSON_UTF8, body=resp_body)
