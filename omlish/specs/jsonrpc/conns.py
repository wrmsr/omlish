import builtins
import json
import typing as ta
import uuid

import anyio.abc

from ... import lang
from ... import marshal as msh
from ...asyncs import anyio as aiu
from ...io.buffers import DelimitingBuffer
from .types import Error
from .types import Id
from .types import Message
from .types import NotSpecified
from .types import Object
from .types import Request
from .types import Response
from .types import detect_message_type
from .types import notification
from .types import request


##


@lang.cached_function
def _create_id() -> str:
    return str(uuid.uuid4())


class JsonrpcConnection:
    def __init__(
            self,
            tg: anyio.abc.TaskGroup,
            stream: anyio.abc.ByteStream,
            *,
            notification_handler: ta.Callable[[Request], ta.Awaitable[None]] | None = None,
            default_timeout: float | None = 30.0,
    ) -> None:
        super().__init__()

        self._tg = tg
        self._stream = stream
        self._notification_handler = notification_handler
        self._default_timeout = default_timeout

        self._buf = DelimitingBuffer(b'\n')
        self._response_futures_by_id: dict[Id, aiu.Future[Response]] = {}
        self._send_lock = anyio.Lock()
        self._received_eof = False
        self._running = True

    #

    class Error(Exception):
        """Base class for JSON-RPC related errors."""

    class TimeoutError(Error, builtins.TimeoutError):  # noqa
        """Raised when a request times out."""

    class ConnectionError(Error, builtins.ConnectionError):  # noqa
        """Raised when there are connection-related issues."""

    class ProtocolError(Error):
        """Raised when there are protocol-related issues."""

    #

    async def __aenter__(self) -> 'JsonrpcConnection':
        await self._tg.start(self._receive_loop)
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        self._running = False

    ##

    async def _handle_message(self, msg: Message) -> None:
        if isinstance(msg, Response):
            msg_id = msg.id
            try:
                resp_fut = self._response_futures_by_id[msg_id]
            except KeyError:
                raise NotImplementedError from None
            resp_fut.set_value(msg)

        elif isinstance(msg, Request):
            if msg.is_notification:
                if (mh := self._notification_handler) is not None:
                    await mh(msg)

            else:
                raise NotImplementedError

        else:
            raise TypeError(msg)

    #

    CLOSED_EXCEPTIONS: ta.ClassVar[tuple[type[Exception], ...]] = (
        anyio.ClosedResourceError,
        anyio.EndOfStream,
    )

    ERROR_EXCEPTIONS: ta.ClassVar[tuple[type[Exception], ...]] = (
        OSError,
        anyio.BrokenResourceError,
    )

    async def _receive_message_batch(self) -> list[Message] | None:
        if self._received_eof:
            return None

        while True:
            try:
                data = await self._stream.receive()
            except self.CLOSED_EXCEPTIONS:
                data = b''
            except self.ERROR_EXCEPTIONS as e:
                raise JsonrpcConnection.ConnectionError('Failed to receive message') from e

            if not data:
                self._received_eof = True

            lines = list(self._buf.feed(data))
            if lines:
                break

            if not data:
                return None

        msgs: list[Message] = []
        for line in lines:
            if isinstance(line, DelimitingBuffer.Incomplete):
                raise ConnectionError('Received incomplete message')

            try:
                dct = json.loads(line.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                raise JsonrpcConnection.ProtocolError from e

            mcls = detect_message_type(dct)
            try:
                msg = msh.unmarshal(dct, mcls)
            except Exception as e:
                raise JsonrpcConnection.ProtocolError from e

            msgs.append(msg)

        return msgs

    async def _receive_loop(
            self,
            *,
            task_status: anyio.abc.TaskStatus[ta.Any] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        task_status.started()

        while self._running:
            msgs = await self._receive_message_batch()
            if msgs is None:
                break

            for msg in msgs:
                await self._handle_message(msg)

    ##

    async def send_message(self, msg: Message) -> None:
        async with self._send_lock:
            try:
                await self._stream.send(json.dumps(msh.marshal(msg)).encode() + b'\n')
            except self.ERROR_EXCEPTIONS as e:
                raise ConnectionError('Failed to send message') from e

    #

    async def request(
            self,
            method: str,
            params: Object | None = None,
            *,
            timeout: float | None = None,
    ) -> ta.Any:
        msg_id = _create_id()
        req = request(msg_id, method, params)

        fut = aiu.create_future[Response]()
        self._response_futures_by_id[msg_id] = fut

        try:
            await self.send_message(req)

            timeout_val = timeout if timeout is not None else self._default_timeout
            try:
                with anyio.fail_after(timeout_val):
                    await fut
            except TimeoutError as e:
                raise JsonrpcConnection.TimeoutError(f'Request timed out after {timeout_val} seconds') from e

            response = fut.outcome.must().unwrap()

            if response.error is not NotSpecified:
                error = ta.cast(Error, response.error)
                raise JsonrpcConnection.Error(f'Error {error.code}: {error.message}')

            return response.result

        finally:
            self._response_futures_by_id.pop(msg_id, None)  # noqa

    async def notify(self, method: str, params: Object | None = None) -> None:
        msg = notification(method, params)
        await self.send_message(msg)
