import json
import typing as ta

import anyio
import anyio.abc
import pytest

from omlish import marshal as msh
from omlish.specs.jsonrpc.types import Error
from omlish.specs.jsonrpc.types import Response
from omlish.specs.jsonrpc.types import notification
from omlish.specs.jsonrpc.types import result

from ..client import JsonRpcClient
from ..client import JsonRpcConnectionError
from ..client import JsonRpcError
from ..client import JsonRpcTimeoutError


##


class MockStream:
    """A mock stream that simulates a bidirectional byte stream."""

    def __init__(self) -> None:
        super().__init__()

        self.send_queue: anyio.abc.ObjectReceiveStream[bytes]
        self.send_queue_tx: anyio.abc.ObjectSendStream[bytes]
        self.receive_queue: anyio.abc.ObjectReceiveStream[bytes]
        self.receive_queue_tx: anyio.abc.ObjectSendStream[bytes]
        self.closed = False

        self.send_queue_tx, self.send_queue = anyio.create_memory_object_stream[bytes]()
        self.receive_queue_tx, self.receive_queue = anyio.create_memory_object_stream[bytes]()

    async def send(self, data: bytes) -> None:
        if self.closed:
            raise anyio.BrokenResourceError
        await self.send_queue_tx.send(data)

    async def receive(self) -> bytes:
        if self.closed:
            raise anyio.BrokenResourceError
        try:
            return await self.receive_queue.receive()
        except anyio.EndOfStream:
            return b''

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def stream() -> ta.AsyncIterator[MockStream]:
    s = MockStream()
    yield s
    s.close()


@pytest.fixture
def notification_handler() -> ta.Callable[[str, ta.Any], ta.Awaitable[None]]:
    notifications: list[tuple[str, ta.Any]] = []

    async def handler(method: str, params: ta.Any) -> None:
        notifications.append((method, params))

    handler.notifications = notifications  # type: ignore
    return handler


@pytest.mark.asyncs
async def test_request_response(stream: MockStream) -> None:
    """Test basic request-response functionality."""

    async with anyio.create_task_group() as tg:
        async with JsonRpcClient(tg, stream) as client:
            # Start request in background
            async def make_request() -> None:
                result = await client.request('test_method', {'param': 'value'})
                assert result == 'test_response'

            tg.start_soon(make_request)

            # Get the request from the mock stream
            request_data = await stream.send_queue.receive()
            request_obj = json.loads(request_data.decode())

            # Verify request format
            assert request_obj['method'] == 'test_method'
            assert request_obj['params'] == {'param': 'value'}
            assert 'id' in request_obj

            # Send response
            response = result(request_obj['id'], 'test_response')
            await stream.receive_queue_tx.send(json.dumps(msh.marshal(response)).encode())


@pytest.mark.asyncs
async def test_notification(stream: MockStream, notification_handler: ta.Any) -> None:
    """Test notification handling."""

    async with anyio.create_task_group() as tg:
        async with JsonRpcClient(tg, stream, notification_handler=notification_handler) as client:  # noqa
            # Send notification from server
            notif = notification('test_notification', {'data': 'value'})
            await stream.receive_queue_tx.send(json.dumps(msh.marshal(notif)).encode())

            # Wait a bit for notification to be processed
            await anyio.sleep(0.1)

            # Verify notification was received
            assert len(notification_handler.notifications) == 1
            method, params = notification_handler.notifications[0]
            assert method == 'test_notification'
            assert params == {'data': 'value'}


@pytest.mark.asyncs
async def test_client_notification(stream: MockStream) -> None:
    """Test sending notifications from client."""
    async with anyio.create_task_group() as tg:
        async with JsonRpcClient(tg, stream) as client:
            await client.notify('test_method', {'param': 'value'})

            # Get the notification from the mock stream
            notif_data = await stream.send_queue.receive()
            notif_obj = json.loads(notif_data.decode())

            # Verify notification format
            assert notif_obj['method'] == 'test_method'
            assert notif_obj['params'] == {'param': 'value'}
            assert 'id' not in notif_obj


@pytest.mark.asyncs
async def test_request_timeout(stream: MockStream) -> None:
    """Test request timeout handling."""

    async with anyio.create_task_group() as tg:
        async with JsonRpcClient(tg, stream, default_timeout=0.1) as client:
            with pytest.raises(JsonRpcTimeoutError):
                await client.request('test_method')


@pytest.mark.asyncs
async def test_connection_error(stream: MockStream) -> None:
    """Test connection error handling."""

    async with anyio.create_task_group() as tg:
        async with JsonRpcClient(tg, stream) as client:
            stream.close()
            with pytest.raises(JsonRpcConnectionError):
                await client.request('test_method')


@pytest.mark.asyncs
async def test_error_response(stream: MockStream) -> None:
    """Test error response handling."""

    async with anyio.create_task_group() as tg:
        async with JsonRpcClient(tg, stream) as client:
            # Start request in background
            async def make_request() -> None:
                with pytest.raises(JsonRpcError) as exc_info:
                    await client.request('test_method')
                assert 'Test error' in str(exc_info.value)

            tg.start_soon(make_request)

            # Get the request from the mock stream
            request_data = await stream.send_queue.receive()
            request_obj = json.loads(request_data.decode())

            # Send error response
            error_response = Response(
                request_obj['id'],
                error=Error(code=1, message='Test error'),
            )
            await stream.receive_queue_tx.send(json.dumps(msh.marshal(error_response)).encode())


@pytest.mark.asyncs
async def test_concurrent_requests(stream: MockStream) -> None:
    """Test handling multiple concurrent requests."""

    async with anyio.create_task_group() as tg:
        async with JsonRpcClient(tg, stream) as client:
            results: dict[str, str] = {}

            async def make_request(method: str) -> None:
                results[method] = await client.request(method)

            # Start multiple requests
            for i in range(3):
                method = f'method_{i}'
                tg.start_soon(make_request, method)

            # Handle each request
            for _ in range(3):
                request_data = await stream.send_queue.receive()
                request_obj = json.loads(request_data.decode())

                # Send response
                response = result(request_obj['id'], f"response_{request_obj['method']}")
                await stream.receive_queue_tx.send(json.dumps(msh.marshal(response)).encode())

            # Verify all requests got correct responses
            assert len(results) == 3
            for i in range(3):
                assert results[f'method_{i}'] == f'response_method_{i}'
