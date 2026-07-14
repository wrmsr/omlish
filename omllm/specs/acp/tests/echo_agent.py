#!/usr/bin/env python3
import abc
import argparse
import asyncio
import dataclasses as dc
import json
import os.path
import sys
import traceback
import typing as ta
import uuid

from omcore import marshal as msh

from .. import protocol


JsonObject: ta.TypeAlias = ta.Mapping[str, ta.Any]
RequestId: ta.TypeAlias = str | int | None


##
# tiny ACP-ish schema subset


def _put_meta(d: JsonObject, field_meta: JsonObject | None) -> JsonObject:
    if field_meta is not None:
        d = {**d, '_meta': field_meta}
    return d


@dc.dataclass(slots=True)
class TextContentBlock:
    text: str
    annotations: JsonObject | None = None
    field_meta: JsonObject | None = None

    @classmethod
    def from_json(cls, obj: ta.Any) -> TextContentBlock | None:
        if not isinstance(obj, dict):
            return None

        typ = obj.get('type')
        if typ is not None and typ != 'text':
            return None

        text = obj.get('text')
        if not isinstance(text, str):
            return None

        return cls(
            text=text,
            annotations=obj.get('annotations') if isinstance(obj.get('annotations'), dict) else None,
            field_meta=obj.get('_meta') if isinstance(obj.get('_meta'), dict) else None,
        )

    def to_json(self) -> JsonObject:
        d: dict[str, ta.Any] = {
            'type': 'text',
            'text': self.text,
        }
        if self.annotations is not None:
            d['annotations'] = self.annotations
        return _put_meta(d, self.field_meta)


@dc.dataclass(slots=True)
class AgentMessageChunk:
    content: TextContentBlock
    field_meta: JsonObject | None = None

    def to_json(self) -> JsonObject:
        d: JsonObject = {
            'sessionUpdate': 'agent_message_chunk',
            'content': self.content.to_json(),
        }
        return _put_meta(d, self.field_meta)


@dc.dataclass(slots=True)
class InitializeResponse:
    protocol_version: int
    agent_info: JsonObject | None = None

    def to_json(self) -> JsonObject:
        return {
            'protocolVersion': self.protocol_version,
            'agentCapabilities': {
                'loadSession': False,
                'mcpCapabilities': {
                    'http': False,
                    'sse': False,
                },
                'promptCapabilities': {
                    'audio': False,
                    'embeddedContext': False,
                    'image': False,
                },
                'sessionCapabilities': {},
            },
            'authMethods': [],
            'agentInfo': self.agent_info or {
                'name': 'zero-dep-echo-agent',
                'version': '0.1.0',
            },
        }


@dc.dataclass(slots=True)
class NewSessionResponse:
    session_id: str

    def to_json(self) -> JsonObject:
        return {'sessionId': self.session_id}


@dc.dataclass(slots=True)
class PromptResponse:
    stop_reason: str = 'end_turn'
    user_message_id: str | None = None

    def to_json(self) -> JsonObject:
        d: dict[str, ta.Any] = {'stopReason': self.stop_reason}

        # Present in the Python SDK echo example you pasted. Some ACP schema versions do not include this field; clients
        # that do not care should ignore it.
        if self.user_message_id is not None:
            d['userMessageId'] = self.user_message_id

        return d


##
# IO Abstraction


class AcpTransport(abc.ABC):
    """Abstract transport layer for ACP server communication."""

    @abc.abstractmethod
    async def read_message(self) -> bytes | None:
        """Read a single message. Returns None on EOF/close."""

        raise NotImplementedError

    @abc.abstractmethod
    async def write_message(self, data: bytes) -> None:
        """Write a single message."""

        raise NotImplementedError


class AcpServer(abc.ABC):
    @abc.abstractmethod
    async def run_server(self, handler: ta.Callable[[AcpTransport], ta.Awaitable[None]]) -> None:
        """Run the server and handle connections. For stdio, this just calls handler once."""

        raise NotImplementedError


class StdioAcp(AcpTransport, AcpServer):
    """Transport using stdin/stdout for communication."""

    def __init__(self) -> None:
        super().__init__()

    async def read_message(self) -> bytes | None:
        line = await asyncio.to_thread(sys.stdin.buffer.readline)
        if not line:
            return None
        return line

    async def write_message(self, data: bytes) -> None:
        await asyncio.to_thread(sys.stdout.buffer.write, data)
        await asyncio.to_thread(sys.stdout.buffer.flush)

    async def run_server(self, handler: ta.Callable[[AcpTransport], ta.Awaitable[None]]) -> None:
        await handler(self)


class UnixSocketAcpServer(AcpServer):
    """Transport using Unix domain sockets for communication."""

    def __init__(self, socket_path: str) -> None:  # noqa
        super().__init__()

        self._socket_path = socket_path

    class Transport(AcpTransport):
        def __init__(
                self,
                reader: asyncio.StreamReader,
                writer: asyncio.StreamWriter,
        ) -> None:
            super().__init__()

            self._reader = reader
            self._writer = writer

        async def read_message(self) -> bytes | None:
            line = await self._reader.readline()
            if not line:
                return None
            return line

        async def write_message(self, data: bytes) -> None:
            if self._writer is None:
                raise RuntimeError('No active connection')

            self._writer.write(data)
            await self._writer.drain()

    async def run_server(self, handler: ta.Callable[[AcpTransport], ta.Awaitable[None]]) -> None:
        if os.path.exists(self._socket_path):
            os.unlink(self._socket_path)

        async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            try:
                await handler(self.Transport(reader, writer))
            finally:
                writer.close()
                await writer.wait_closed()

        server = await asyncio.start_unix_server(handle_client, path=self._socket_path)
        print(f'Unix socket ACP server listening on {self._socket_path}', file=sys.stderr)

        async with server:
            await server.serve_forever()


##
# JSON-RPC plumbing


class JsonRpcError(Exception):
    def __init__(self, code: int, message: str, data: ta.Any = None) -> None:
        super().__init__(message)

        self.code = code
        self.message = message
        self.data = data


PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


_MISSING = object()


def get_param(
    params: JsonObject,
    camel_name: str,
    snake_name: str | None = None,
    default: ta.Any = _MISSING,
) -> ta.Any:
    if camel_name in params:
        return params[camel_name]
    if snake_name is not None and snake_name in params:
        return params[snake_name]
    if default is not _MISSING:
        return default
    raise JsonRpcError(INVALID_PARAMS, f'Missing required param: {camel_name}')


def ensure_params(raw: ta.Any) -> JsonObject:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise JsonRpcError(INVALID_PARAMS, 'params must be an object')
    return raw


class JsonRpcPeer:
    def __init__(self, transport: AcpTransport) -> None:
        super().__init__()

        self._transport = transport
        self._write_lock = asyncio.Lock()

    async def send(self, msg: JsonObject) -> None:
        data = json.dumps(msg, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n'
        async with self._write_lock:
            await self._transport.write_message(data)

    async def send_result(self, request_id: RequestId, result: ta.Any) -> None:
        await self.send({
            'jsonrpc': '2.0',
            'id': request_id,
            'result': result,
        })

    async def send_error(
        self,
        request_id: RequestId,
        code: int,
        message: str,
        data: ta.Any = None,
    ) -> None:
        err: dict[str, ta.Any] = {
            'code': code,
            'message': message,
        }
        if data is not None:
            err['data'] = data

        await self.send({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': err,
        })

    async def send_notification(self, method: str, params: JsonObject) -> None:
        await self.send({
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
        })


##
# echo ACP agent


class EchoAcpHandler:
    def __init__(self, transport: AcpTransport) -> None:
        super().__init__()

        self._transport = transport
        self._peer = JsonRpcPeer(transport)
        self._sessions: set[str] = set()

    async def run(self) -> None:
        while True:
            line = await self._transport.read_message()
            if not line:
                return

            line = line.strip()
            if not line:
                continue

            await self._handle_line(line)

    async def _handle_line(self, line: bytes) -> None:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            await self._peer.send_error(None, PARSE_ERROR, 'Parse error', str(e))
            return

        print(json.dumps(msg, indent=2, separators=(', ', ': ')), file=sys.stderr)

        if not isinstance(msg, dict):
            await self._peer.send_error(None, INVALID_REQUEST, 'JSON-RPC message must be an object')
            return

        request_id = msg.get('id')
        is_request = 'id' in msg

        try:
            # Ignore responses from the client. This echo agent never sends JSON-RPC requests, only notifications, so
            # there is nothing to match.
            if 'method' not in msg and ('result' in msg or 'error' in msg):
                return

            if msg.get('jsonrpc') != '2.0':
                raise JsonRpcError(INVALID_REQUEST, "jsonrpc must be '2.0'")

            method = msg.get('method')
            if not isinstance(method, str):
                raise JsonRpcError(INVALID_REQUEST, 'method must be a string')

            result = await self._dispatch(method, ensure_params(msg.get('params')))

        except JsonRpcError as e:
            if is_request:
                await self._peer.send_error(request_id, e.code, e.message, e.data)
            return

        except Exception as e:  # noqa
            print('Internal ACP server error:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            if is_request:
                await self._peer.send_error(request_id, INTERNAL_ERROR, 'Internal error', str(e))
            return

        if is_request:
            print(json.dumps(result, indent=2, separators=(', ', ': ')), file=sys.stderr)
            await self._peer.send_result(request_id, result)

    async def _dispatch(self, method: str, params: JsonObject) -> ta.Any:
        match method:
            case 'initialize':
                return await self.initialize(params)

            case 'session/new':
                return await self.new_session(params)

            case 'session/prompt':
                return await self.prompt(params)

            case 'session/cancel':
                # This echo agent has no long-running work to cancel. If a client sends this as a notification, no
                # response is sent by JSON-RPC.
                return {}

            case _:
                raise JsonRpcError(METHOD_NOT_FOUND, f'Method not found: {method}')

    async def initialize(self, params: JsonObject) -> JsonObject:
        protocol_version = get_param(params, 'protocolVersion', 'protocol_version')
        if not isinstance(protocol_version, int):
            raise JsonRpcError(INVALID_PARAMS, 'protocolVersion must be an integer')

        return msh.marshal(protocol.InitializeResponse(protocol_version=protocol_version))  # type: ignore

    async def new_session(self, params: JsonObject) -> JsonObject:
        # Equivalent to the SDK sample: accept cwd/additionalDirectories/mcpServers but do not do anything with them.
        cwd = get_param(params, 'cwd', default=None)
        if cwd is not None and not isinstance(cwd, str):
            raise JsonRpcError(INVALID_PARAMS, 'cwd must be a string')

        session_id = uuid.uuid7().hex
        self._sessions.add(session_id)
        return NewSessionResponse(session_id=session_id).to_json()

    async def prompt(self, params: JsonObject) -> JsonObject:
        session_id = get_param(params, 'sessionId', 'session_id')
        if not isinstance(session_id, str):
            raise JsonRpcError(INVALID_PARAMS, 'sessionId must be a string')
        if session_id not in self._sessions:
            raise JsonRpcError(INVALID_PARAMS, f'Unknown sessionId: {session_id}')

        prompt = get_param(params, 'prompt')
        if not isinstance(prompt, list):
            raise JsonRpcError(INVALID_PARAMS, 'prompt must be a list')

        message_id = get_param(params, 'messageId', 'message_id', default=None)
        if message_id is not None and not isinstance(message_id, str):
            raise JsonRpcError(INVALID_PARAMS, 'messageId must be a string when present')

        for raw_block in prompt:
            block = TextContentBlock.from_json(raw_block)
            if block is None:
                # Per your requirement: only TextContentBlock is handled.
                continue

            echoed = TextContentBlock(
                text=block.text,
                field_meta={'echo': True},
            )
            chunk = AgentMessageChunk(
                content=echoed,
                field_meta={'echo': True},
            )

            await self.session_update(
                session_id=session_id,
                update=chunk,
                source='echo_agent',
            )

        return PromptResponse(
            stop_reason='end_turn',
            user_message_id=message_id,
        ).to_json()

    async def session_update(
        self,
        *,
        session_id: str,
        update: AgentMessageChunk,
        source: str | None = None,
    ) -> None:
        params: dict[str, ta.Any] = {
            'sessionId': session_id,
            'update': update.to_json(),
        }

        # The SDK echo passes source="echo_agent". The current public schema does not show a top-level source field on
        # SessionNotification, so keep it in ACP's reserved extensibility metadata instead of making the notification
        # shape stricter-client-hostile.
        if source is not None:
            params['_meta'] = {'source': source}

        await self._peer.send_notification('session/update', params)


async def main() -> None:
    parser = argparse.ArgumentParser(description='Zero-dependency echo ACP agent server')
    subparsers = parser.add_subparsers()
    parser.set_defaults(_cmd=None)

    serve_parser = subparsers.add_parser('serve')
    serve_parser.set_defaults(_cmd='serve')
    serve_parser.add_argument(
        '-t',
        '--transport',
        choices=['stdio', 'unix'],
        default='stdio',
        help='Transport type to use (default: stdio)',
    )
    serve_parser.add_argument(
        '-s',
        '--socket',
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), '.acp.sock')),
        help='Socket path for Unix socket transport',
    )

    args = parser.parse_args()

    match args._cmd:  # noqa
        case 'serve':
            server: AcpServer
            match args.transport:
                case 'stdio':
                    server = StdioAcp()

                case 'unix':
                    server = UnixSocketAcpServer(args.socket)

                case _:
                    raise ValueError(f'Unknown transport: {args.transport}')

            async def handler(t: AcpTransport) -> None:
                await EchoAcpHandler(t).run()

            await server.run_server(handler)

        case None:
            parser.print_help()

        case _:
            raise RuntimeError('invalid command specified')


if __name__ == '__main__':
    asyncio.run(main())
