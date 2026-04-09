import asyncio
import builtins
import contextlib
import json
import typing as ta
import uuid

from ... import check
from ... import lang
from ... import marshal as msh
from ...io.streams.scanning import ScanningByteStreamBuffer
from ...io.streams.segmented import SegmentedByteStreamBuffer
from ...io.streams.utils import ByteStreamBuffers
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


class AsyncByteStream(ta.Protocol):
    async def send(self, data: bytes) -> None: ...
    async def receive(self) -> bytes: ...


@ta.final
class QueueByteStream:
    def __init__(
            self,
            rx: asyncio.Queue[bytes | None],
            tx: asyncio.Queue[bytes | None],
    ) -> None:
        self._rx = rx
        self._tx = tx

    async def send(self, data: bytes) -> None:
        await self._tx.put(data)

    async def receive(self) -> bytes:
        item = await self._rx.get()
        if item is None:
            return b''  # EOF
        return item


##


@ta.final
class AsyncioStreamAdapter:
    def __init__(
            self,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
            *,
            read_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._reader = reader
        self._writer = writer
        self._read_size = read_size

    async def send(self, data: bytes) -> None:
        self._writer.write(data)
        await self._writer.drain()

    async def receive(self) -> bytes:
        return await self._reader.read(self._read_size)

    async def aclose(self) -> None:
        self._writer.close()
        await self._writer.wait_closed()


##


class JsonrpcConnection:
    def __init__(
            self,
            stream: AsyncByteStream,
            *,
            request_handler: ta.Callable[[JsonrpcConnection, Request], ta.Awaitable[None]] | None = None,
            notification_handler: ta.Callable[[JsonrpcConnection, Request], ta.Awaitable[None]] | None = None,
            default_timeout: float | None = 30.,
            id_creator: ta.Callable[[], Id] | None = None,
    ) -> None:
        super().__init__()

        self._stream = stream
        self._request_handler = request_handler
        self._notification_handler = notification_handler
        self._default_timeout = default_timeout
        if id_creator is None:
            id_creator = self.default_create_id
        self._create_id = id_creator

        self._raw_buf = SegmentedByteStreamBuffer(chunk_size=0x4000)
        self._buf = ScanningByteStreamBuffer(self._raw_buf)
        self._response_futures_by_id: dict[Id, asyncio.Future[Response]] = {}
        self._send_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._receive_started = asyncio.Event()
        self._receive_task: asyncio.Task[None] | None = None
        self._received_eof = False

    @classmethod
    def default_create_id(cls) -> Id:
        return str(uuid.uuid4())

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

    async def __aenter__(self) -> ta.Self:
        check.state(self._receive_task is None)

        self._receive_task = asyncio.create_task(
            self._receive_loop(),
            name=f'{self.__class__.__name__}._receive_loop',
        )

        await self._receive_started.wait()
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        self._shutdown_event.set()

        task = self._receive_task
        self._receive_task = None

        if task is not None:
            if not task.done():
                task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                if exc_type is None:
                    raise

        aclose = getattr(self._stream, 'aclose', None)
        if aclose is not None:
            await aclose()

    ##

    async def _handle_message(self, msg: Message) -> None:
        if isinstance(msg, Response):
            msg_id = msg.id
            try:
                resp_fut = self._response_futures_by_id[msg_id]
            except KeyError:
                raise NotImplementedError from None

            if not resp_fut.done():
                resp_fut.set_result(msg)

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
        EOFError,
        asyncio.IncompleteReadError,
    )

    ERROR_EXCEPTIONS: ta.ClassVar[tuple[type[Exception], ...]] = (
        OSError,
        BrokenPipeError,
        ConnectionResetError,
    )

    async def _wait_shutdown_or_receive(self) -> bytes | None:
        recv_task = asyncio.create_task(self._stream.receive())
        shutdown_task = asyncio.create_task(self._shutdown_event.wait())

        try:
            done, pending = await asyncio.wait(
                {recv_task, shutdown_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            if shutdown_task in done:
                return None

            return await recv_task

        finally:
            for t in (recv_task, shutdown_task):
                if not t.done():
                    t.cancel()

            for t in (recv_task, shutdown_task):
                with contextlib.suppress(asyncio.CancelledError):
                    await t

    async def _receive_message_batch(self) -> list[Message] | None:
        check.state(not self._received_eof)

        if self._shutdown_event.is_set():
            return None

        while True:
            try:
                data = await self._wait_shutdown_or_receive()
            except self.CLOSED_EXCEPTIONS:
                data = b''
            except self.ERROR_EXCEPTIONS as e:
                raise self.ConnectionError('Failed to receive message') from e

            if data is None:
                return None

            if not data:
                self._received_eof = True

            self._buf.write(data)
            lines = ByteStreamBuffers.split(self._buf, b'\n')

            if not data:
                if len(self._buf):
                    raise self.ConnectionError('Received incomplete message')

            if lines:
                break

            if not data:
                return None

        msgs: list[Message] = []
        for linev in lines:
            line = linev.tobytes()

            try:
                dct = json.loads(line.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                raise self.ProtocolError from e

            mcls = detect_message_type(dct)
            try:
                msg = msh.unmarshal(dct, mcls)
            except Exception as e:
                raise self.ProtocolError from e

            msgs.append(msg)

        return msgs

    async def _receive_loop(self) -> None:
        self._receive_started.set()

        exc: Exception | None = None

        try:
            while not self._shutdown_event.is_set():
                msgs = await self._receive_message_batch()
                if msgs is None:
                    break

                for msg in msgs:
                    await self._handle_message(msg)

        except asyncio.CancelledError:
            raise

        except Exception as e:
            exc = e
            raise

        finally:
            if exc is None:
                exc = self.ConnectionError('Connection closed')

            for fut in self._response_futures_by_id.values():
                if not fut.done():
                    fut.set_exception(exc)

    ##

    async def send_message(self, msg: Message) -> None:
        async with self._send_lock:
            try:
                await self._stream.send(json.dumps(msh.marshal(msg)).encode() + b'\n')  # noqa
            except self.ERROR_EXCEPTIONS as e:
                raise self.ConnectionError('Failed to send message') from e

    #

    async def request(
            self,
            method: str,
            params: Object | None = None,
            *,
            timeout: lang.TimeoutLike | None = lang.Timeout.DEFAULT,
    ) -> ta.Any:
        msg_id = self._create_id()
        req = request(msg_id, method, params)

        fut = asyncio.get_running_loop().create_future()
        self._response_futures_by_id[msg_id] = fut

        try:
            await self.send_message(req)

            timeout_val = lang.Timeout.of(timeout, self._default_timeout)
            timeout_s = timeout_val.or_(None)

            try:
                if timeout_s is None:
                    response = await fut
                else:
                    async with asyncio.timeout(timeout_s):
                        response = await fut

            except TimeoutError as e:
                raise self.TimeoutError(f'Request timed out after {timeout_val} seconds') from e

            if response.error is not NotSpecified:
                error = ta.cast(Error, response.error)
                raise self.Error(f'Error {error.code}: {error.message}')

            return response.result

        finally:
            self._response_futures_by_id.pop(msg_id, None)
            if not fut.done():
                fut.cancel()

    async def notify(self, method: str, params: Object | None = None) -> None:
        msg = notification(method, params)
        await self.send_message(msg)
