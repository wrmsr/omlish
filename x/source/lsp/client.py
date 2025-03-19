import dataclasses as dc
import functools
import json
import typing as ta

from omlish import marshal as msh
from omlish.asyncs.buffers import AsyncBufferedReader
from omlish.specs import jsonrpc as jr

from .framing import format_http_framed_message
from .framing import read_http_framed_message


##


class LspClient:
    def __init__(
            self,
            send: ta.Callable[[bytes], ta.Awaitable[None]],
            receive: ta.Callable[[], ta.Awaitable[bytes]],
    ) -> None:
        super().__init__()

        self._send = send
        self._receive = receive

        self._last_id = 0

        self._reader = AsyncBufferedReader(receive)
        self._read_content = functools.partial(read_http_framed_message, self._reader)

    #

    def _next_id(self) -> int:
        self._last_id += 1
        return self._last_id

    #

    async def send(self, request: jr.Request) -> None:
        marshalled = msh.marshal(request)
        content = json.dumps(marshalled).encode('utf-8')
        message = format_http_framed_message(content)
        await self._send(message)

    async def request(self, method: str, params: ta.Any = None) -> dict[str, ta.Any]:
        if dc.is_dataclass(params):
            params = msh.marshal(params)
        await self.send(jr.request(
            msg_id := self._next_id(),
            method,
            params,
        ))
        return await self.read_response(msg_id)

    async def notify(self, method: str, params: ta.Any = None) -> None:
        if dc.is_dataclass(params):
            params = msh.marshal(params)
        await self.send(jr.notification(
            method,
            params,
        ))

    #

    async def read_message(self) -> dict[str, ta.Any] | None:
        content, _ = await self._read_content()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print('Invalid JSON response from LSP server.')
            return None

    async def read_response(self, msg_id: int) -> dict[str, ta.Any]:
        while True:
            msg = await self.read_message()
            if msg is None:
                raise RuntimeError
            if msg.get('id') == msg_id:
                return msg
