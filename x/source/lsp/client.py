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

    async def request(self, method: str, params: ta.Any = None) -> jr.Response:
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

    async def read(self) -> jr.Message:
        content, _ = await self._read_content()
        dct = json.loads(content)
        cls = jr.detect_message_type(dct)
        return msh.unmarshal(dct, cls)

    async def read_response(self, msg_id: int) -> jr.Response:
        while True:
            msg = await self.read()
            if isinstance(msg, jr.Response) and msg.id == msg_id:
                return msg
