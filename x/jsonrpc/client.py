"""
TODO:
 - split connection and dispatcher
"""
import json
import typing as ta
import uuid

import anyio.abc

from omlish import lang
from omlish import marshal as msh
from omlish.asyncs import anyio as aiu
from omlish.io.buffers import DelimitingBuffer
from omlish.specs import jsonrpc as jr


##


class JsonrpcError(Exception):
    """Base class for JSON-RPC related errors."""


class JsonrpcTimeoutError(JsonrpcError):
    """Raised when a request times out."""


class JsonrpcConnectionError(JsonrpcError):
    """Raised when there are connection-related issues."""


class JsonrpcProtocolError(JsonrpcError):
    """Raised when there are protocol-related issues."""


##


@lang.cached_function
def _create_id() -> str:
    return str(uuid.uuid4())


CONNECTION_ERROR_EXCEPTIONS: tuple[type[Exception], ...] = (
    OSError,
    anyio.BrokenResourceError,
)


class JsonrpcClient:
    def __init__(
            self,
            tg: anyio.abc.TaskGroup,
            stream: anyio.abc.ByteStream,
            *,
            notification_handler: ta.Callable[[jr.Request], ta.Awaitable[None]] | None = None,
            default_timeout: float | None = 30.0,
    ) -> None:
        super().__init__()

        self._tg = tg
        self._stream = stream
        self._notification_handler = notification_handler
        self._default_timeout = default_timeout

        self._buf = DelimitingBuffer(b'\n')
        self._response_futures_by_id: dict[jr.Id, aiu.Future[jr.Response]] = {}
        self._send_lock = anyio.Lock()
        self._received_eof = False
        self._running = True

    #

    async def __aenter__(self) -> 'JsonrpcClient':
        await self._tg.start(self._receive_loop)
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        self._running = False

    async def _receive(self) -> list[jr.Message] | None:
        if self._received_eof:
            return None

        while True:
            try:
                data = await self._stream.receive()
            except CONNECTION_ERROR_EXCEPTIONS as e:
                raise JsonrpcConnectionError('Failed to receive message') from e

            if not data:
                self._received_eof = True

            lines = list(self._buf.feed(data))
            if lines:
                break

            if not data:
                return None

        msgs: list[jr.Message] = []
        for line in lines:
            if isinstance(line, DelimitingBuffer.Incomplete):
                raise JsonrpcConnectionError('Received incomplete message')

            try:
                dct = json.loads(line.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                raise JsonrpcProtocolError from e

            mcls = jr.detect_message_type(dct)
            try:
                msg = msh.unmarshal(dct, mcls)
            except Exception as e:
                raise JsonrpcProtocolError from e

            msgs.append(msg)

        return msgs

    async def _receive_loop(
            self,
            *,
            task_status: anyio.abc.TaskStatus[ta.Any] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        task_status.started()

        while self._running:
            msgs = await self._receive()
            if msgs is None:
                break

            for msg in msgs:
                if isinstance(msg, jr.Response):
                    msg_id = msg.id
                    try:
                        resp_fut = self._response_futures_by_id[msg_id]
                    except KeyError:
                        raise NotImplementedError
                    resp_fut.set_value(msg)

                elif isinstance(msg, jr.Request):
                    if msg.is_notification:
                        if (mh := self._notification_handler) is not None:
                            await mh(msg)

                    else:
                        raise NotImplementedError

                elif isinstance(msg, jr.Error):
                    raise NotImplementedError

                else:
                    raise JsonrpcProtocolError(msg)

    #

    async def _send(self, msg: jr.Message) -> None:
        async with self._send_lock:
            try:
                await self._stream.send(json.dumps(msh.marshal(msg)).encode())
            except CONNECTION_ERROR_EXCEPTIONS as e:
                raise JsonrpcConnectionError('Failed to send message') from e

    async def request(
            self,
            method: str,
            params: jr.Object | None = None,
            *,
            timeout: float | None = None,
    ) -> ta.Any:
        msg_id = _create_id()
        req = jr.request(msg_id, method, params)

        fut = aiu.create_future[jr.Response]()
        self._response_futures_by_id[msg_id] = fut

        try:
            await self._send(req)

            timeout_val = timeout if timeout is not None else self._default_timeout
            try:
                with anyio.fail_after(timeout_val):
                    await fut
            except TimeoutError:
                raise JsonrpcTimeoutError(f'Request timed out after {timeout_val} seconds')

            response = fut.outcome.must().unwrap()

            if response.error is not jr.NotSpecified:
                error = ta.cast(jr.Error, response.error)
                raise JsonrpcError(f'Error {error.code}: {error.message}')

            return response.result

        finally:
            self._response_futures_by_id.pop(msg_id, None)  # noqa

    async def notify(self, method: str, params: jr.Object | None = None) -> None:
        msg = jr.notification(method, params)
        await self._send(msg)
