import builtins
import functools
import json
import typing as ta
import uuid

import anyio.abc

from ... import check
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
            request_handler: ta.Callable[['JsonrpcConnection', Request], ta.Awaitable[None]] | None = None,
            notification_handler: ta.Callable[['JsonrpcConnection', Request], ta.Awaitable[None]] | None = None,
            default_timeout: float | None = 30.,
    ) -> None:
        super().__init__()

        self._tg = tg
        self._stream = stream
        self._request_handler = request_handler
        self._notification_handler = notification_handler
        self._default_timeout = default_timeout

        self._buf = DelimitingBuffer(b'\n')
        self._response_futures_by_id: dict[Id, aiu.Future[Response]] = {}
        self._send_lock = anyio.Lock()
        self._shutdown_event = anyio.Event()
        self._received_eof = False

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
        self._shutdown_event.set()

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
                    await mh(self, msg)

            else:  # noqa
                if (rh := self._request_handler) is not None:
                    await rh(self, msg)

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
        check.state(not self._received_eof)

        if self._shutdown_event.is_set():
            return None

        while True:
            maybe_shutdown: lang.Maybe[bool]
            maybe_data: lang.Maybe[lang.Outcome[bytes]]
            (
                maybe_shutdown,
                maybe_data,
            ) = await aiu.gather(  # type: ignore
                self._shutdown_event.wait,
                functools.partial(lang.acapture, self._stream.receive),
                take_first=True,
            )

            if self._shutdown_event.is_set():
                return None

            try:
                data = maybe_data.must().unwrap()
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

        while not self._shutdown_event.is_set():
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
            timeout: lang.TimeoutLike | None = lang.Timeout.DEFAULT,
    ) -> ta.Any:
        msg_id = _create_id()
        req = request(msg_id, method, params)

        fut = aiu.create_future[Response]()
        self._response_futures_by_id[msg_id] = fut

        try:
            await self.send_message(req)

            timeout_val = lang.Timeout.of(timeout, self._default_timeout)
            try:
                with anyio.fail_after(timeout_val.or_(None)):
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
