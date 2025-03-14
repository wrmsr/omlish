"""
Anyio-based JSON-RPC client implementation supporting concurrent requests, notifications,
timeouts and cancellation.
"""
import contextlib
import json
import typing as ta
import uuid

import anyio
import anyio.abc

from omlish import lang
from omlish import marshal as msh
from omlish.specs.jsonrpc.types import Error
from omlish.specs.jsonrpc.types import Id
from omlish.specs.jsonrpc.types import NotSpecified
from omlish.specs.jsonrpc.types import Object
from omlish.specs.jsonrpc.types import Request
from omlish.specs.jsonrpc.types import Response
from omlish.specs.jsonrpc.types import notification
from omlish.specs.jsonrpc.types import request


##


class JsonRpcError(Exception):
    """Base class for JSON-RPC related errors."""


class JsonRpcTimeoutError(JsonRpcError):
    """Raised when a request times out."""


class JsonRpcConnectionError(JsonRpcError):
    """Raised when there are connection-related issues."""


class JsonRpcProtocolError(JsonRpcError):
    """Raised when there are protocol-related issues."""


##


@lang.cached_function
def _create_id() -> str:
    return str(uuid.uuid4())


class JsonRpcClient:
    """
    Anyio-based JSON-RPC client supporting concurrent requests and notifications.

    Features:
    - Concurrent request handling using anyio
    - Support for notifications (messages without IDs)
    - Request timeouts and cancellation
    - Automatic message ID generation
    - Error handling with custom exceptions
    """

    def __init__(
            self,
            stream: anyio.abc.ByteStream,
            *,
            notification_handler: ta.Callable[[str, Object | None], ta.Awaitable[None]] | None = None,
            default_timeout: float | None = 30.0,
    ) -> None:
        """
        Initialize the JSON-RPC client.

        Args:
            stream: An anyio byte stream for communication
            notification_handler: Optional callback for handling notifications
            default_timeout: Default timeout for requests in seconds
        """

        super().__init__()

        self._stream = stream
        self._notification_handler = notification_handler
        self._default_timeout = default_timeout

        self._pending: dict[Id, anyio.Event] = {}
        self._responses: dict[Id, Response] = {}
        self._send_lock = anyio.Lock()
        self._running = True

        # Start the receive task
        self._receive_task: anyio.abc.TaskGroup | None = None

    async def __aenter__(self) -> 'JsonRpcClient':
        async with anyio.create_task_group() as tg:
            self._receive_task = tg
            tg.start_soon(self._receive_loop)
            return self

    async def __aexit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        self._running = False
        if self._receive_task is not None:
            self._receive_task.cancel_scope.cancel()

    async def _receive_loop(self) -> None:
        """Background task that receives and processes incoming messages."""

        while self._running:
            try:
                data = await self._stream.receive()
                if not data:
                    break

                try:
                    msg = json.loads(data)
                except json.JSONDecodeError:
                    continue

                # Handle response
                if isinstance(msg, dict) and 'id' in msg and msg.get('id') is not NotSpecified:
                    response = msh.unmarshal(msg, Response)
                    msg_id = response.id
                    if msg_id in self._pending:
                        self._responses[msg_id] = response
                        self._pending[msg_id].set()

                # Handle notification
                elif (
                    isinstance(msg, dict) and
                    'method' in msg and
                    ('id' not in msg or msg.get('id') is NotSpecified) and
                    self._notification_handler is not None
                ):
                    req = msh.unmarshal(msg, Request)
                    await self._notification_handler(req.method, req.params)

            except (OSError, anyio.BrokenResourceError):
                break

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
            JsonRpcTimeoutError: If the request times out
            JsonRpcError: If the request fails
            JsonRpcConnectionError: If there are connection issues
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
                    raise JsonRpcConnectionError('Failed to send request') from e

            # Wait for response with timeout
            timeout_val = timeout if timeout is not None else self._default_timeout
            with contextlib.suppress(TimeoutError):
                await anyio.fail_after(timeout_val, event.wait)

            if msg_id not in self._responses:
                raise JsonRpcTimeoutError(f'Request timed out after {timeout_val} seconds')

            response = self._responses[msg_id]

            if response.error is not NotSpecified:
                error = ta.cast(Error, response.error)
                raise JsonRpcError(f'Error {error.code}: {error.message}')

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
            JsonRpcConnectionError: If there are connection issues
        """

        msg = notification(method, params)

        async with self._send_lock:
            try:
                await self._stream.send(json.dumps(msh.marshal(msg)).encode())
            except (OSError, anyio.BrokenResourceError) as e:
                raise JsonRpcConnectionError('Failed to send notification') from e
