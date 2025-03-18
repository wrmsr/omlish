import contextlib
import json
import typing as ta
import uuid

import anyio.abc

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.specs.jsonrpc.types import Error
from omlish.specs.jsonrpc.types import Id
from omlish.specs.jsonrpc.types import NotSpecified
from omlish.specs.jsonrpc.types import Object
from omlish.specs.jsonrpc.types import Request
from omlish.specs.jsonrpc.types import Response
from omlish.specs.jsonrpc.types import detect_message_type
from omlish.specs.jsonrpc.types import notification
from omlish.specs.jsonrpc.types import request


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


class JsonrpcClient:
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

        self._pending: dict[Id, anyio.Event] = {}
        self._responses: dict[Id, Response] = {}
        self._send_lock = anyio.Lock()
        self._running = True

    async def __aenter__(self) -> 'JsonrpcClient':
        await self._tg.start(self._receive_loop)
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        self._running = False

    async def _receive_loop(
            self,
            *,
            task_status: anyio.abc.TaskStatus[ta.Any] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        task_status.started()

        while self._running:
            try:
                data = await self._stream.receive()
                if not data:
                    break

                # FIXME: lines lol
                check.state(b'\n' not in data[:-1])
                check.state(data.endswith(b'\n'))

                try:
                    dct = json.loads(data.decode('utf-8'))
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    raise JsonrpcProtocolError from e

                mcls = detect_message_type(dct)
                try:
                    msg = msh.unmarshal(dct, mcls)
                except Exception as e:
                    raise JsonrpcProtocolError from e

                if isinstance(msg, Response):
                    msg_id = msg.id
                    if msg_id in self._pending:
                        self._responses[msg_id] = msg
                        self._pending[msg_id].set()

                elif isinstance(msg, Request):
                    if msg.is_notification:
                        if (mh := self._notification_handler) is not None:
                            await mh(msg)

                    else:
                        raise NotImplementedError

                elif isinstance(msg, Error):
                    raise NotImplementedError

                else:
                    raise JsonrpcProtocolError(msg)

            # except (OSError, anyio.BrokenResourceError):
            #     break

            except Exception as e:  # noqa
                # FIXME: log / report
                raise

    async def request(
            self,
            method: str,
            params: Object | None = None,
            *,
            timeout: float | None = None,
    ) -> ta.Any:
        """
        Send a JSON-RPC request and wait for the response.

        Args:
            method: The method name to call
            params: Optional parameters for the method
            timeout: Optional timeout override for this specific request

        Returns:
            The result of the request

        Raises:
            JsonrpcTimeoutError: If the request times out
            JsonrpcError: If the request fails
            JsonrpcConnectionError: If there are connection issues
        """

        msg_id = _create_id()
        req = request(msg_id, method, params)

        event = anyio.Event()
        self._pending[msg_id] = event

        try:
            # Send request
            async with self._send_lock:
                try:
                    await self._stream.send(json.dumps(msh.marshal(req)).encode())
                except (OSError, anyio.BrokenResourceError) as e:
                    raise JsonrpcConnectionError('Failed to send request') from e

            # Wait for response with timeout
            timeout_val = timeout if timeout is not None else self._default_timeout
            with contextlib.suppress(TimeoutError):
                await anyio.fail_after(timeout_val, event.wait)

            if msg_id not in self._responses:
                raise JsonrpcTimeoutError(f'Request timed out after {timeout_val} seconds')

            response = self._responses[msg_id]

            if response.error is not NotSpecified:
                error = ta.cast(Error, response.error)
                raise JsonrpcError(f'Error {error.code}: {error.message}')

            return response.result

        finally:
            self._pending.pop(msg_id, None)
            self._responses.pop(msg_id, None)

    async def notify(self, method: str, params: Object | None = None) -> None:
        """
        Send a JSON-RPC notification (a request without an ID).

        Args:
            method: The method name to call
            params: Optional parameters for the method

        Raises:
            JsonrpcConnectionError: If there are connection issues
        """

        msg = notification(method, params)

        async with self._send_lock:
            try:
                await self._stream.send(json.dumps(msh.marshal(msg)).encode())
            except (OSError, anyio.BrokenResourceError) as e:
                raise JsonrpcConnectionError('Failed to send notification') from e
