import asyncio
import typing as ta

from ...asyncio import FlowControlAsyncioStreamDriver
from ...bytes import BytesChannelPipelineFlowControlAdapter
from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import PipelineChannel
from ...flow import FlowControlChannelPipelineHandler
from ...http.requests import HttpRequest
from ...http.requests import HttpRequestBodyAggregator
from ...http.requests import HttpRequestHeadDecoder


##


class KvStoreHandler(ChannelPipelineHandler):
    """
    A minimal KV store over HTTP/1 with one-segment paths.

    - GET /key        -> 200 value or 404
    - POST /key body  -> 201 created/updated, echoes value
    - PUT /key body   -> 200 updated, echoes value
    - DELETE /key     -> 200 deleted or 404

    Constraints:
      - Only accepts single-segment, slashless keys: "/foo" ok, "/foo/bar" rejected.
      - Body is treated as UTF-8 text (replacement), stored as str.
      - Connection: close (we close after each response).
    """

    def __init__(self, items: dict[str, str]) -> None:
        super().__init__()

        self._items = items

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, HttpRequest):
            ctx.feed_in(ctx)
            return

        head = msg.head
        key = self._parse_key(head.target)
        if key is None:
            self._write_response(ctx, 400, b'bad request')
            ctx.channel.feed_close()
            return

        method = head.method.upper()
        if method == 'GET':
            if key not in self._items:
                self._write_response(ctx, 404, b'not found')
            else:
                b = self._items[key].encode('utf-8')
                self._write_response(ctx, 200, b)
            ctx.channel.feed_close()
            return

        if method in ('POST', 'PUT'):
            s = msg.body.decode('utf-8', errors='replace')
            self._items[key] = s
            code = 201 if method == 'POST' else 200
            self._write_response(ctx, code, s.encode('utf-8'))
            ctx.channel.feed_close()
            return

        if method == 'DELETE':
            if key not in self._items:
                self._write_response(ctx, 404, b'not found')
            else:
                del self._items[key]
                self._write_response(ctx, 200, b'deleted')
            ctx.channel.feed_close()
            return

        self._write_response(ctx, 405, b'method not allowed')
        ctx.channel.feed_close()

    def _parse_key(self, target: str) -> str | None:
        # strip querystring
        if '?' in target:
            target = target.split('?', 1)[0]

        if not target.startswith('/'):
            return None

        path = target[1:]
        if not path:
            return None

        if '/' in path:
            return None

        return path

    def _write_response(self, ctx: ChannelPipelineHandlerContext, status: int, body: bytes) -> None:
        reason = {
            200: b'OK',
            201: b'Created',
            400: b'Bad Request',
            404: b'Not Found',
            405: b'Method Not Allowed',
        }.get(status, b'OK')

        resp = (
            b'HTTP/1.1 ' + str(status).encode('ascii') + b' ' + reason + b'\r\n'
            b'Content-Type: text/plain; charset=utf-8\r\n'
            b'Content-Length: ' + str(len(body)).encode('ascii') + b'\r\n'
            b'Connection: close\r\n'
            b'\r\n' +
            body
        )
        ctx.feed_out(resp)


def build_http_kv_channel(
        items: dict[str, str],
        *,
        outbound_capacity: int | None = 1 << 22,
        outbound_overflow_policy: ta.Literal['allow', 'close', 'raise', 'drop'] = 'close',

        max_head: int = 64 << 10,

        max_body: int | None = 1 << 20,
) -> PipelineChannel:
    return PipelineChannel([

        FlowControlChannelPipelineHandler(
            BytesChannelPipelineFlowControlAdapter(),
            FlowControlChannelPipelineHandler.Config(
                outbound_capacity=outbound_capacity,
                outbound_overflow_policy=outbound_overflow_policy,
            ),
        ),

        HttpRequestHeadDecoder(
            max_head=max_head,
            bytes_flow_control=True,
        ),

        HttpRequestBodyAggregator(
            max_body=max_body,
            bytes_flow_control=True,
        ),

        KvStoreHandler(items),

    ])


async def serve_kv(
        *,
        host: str = '127.0.0.1',
        port: int = 8087,
) -> None:
    """
    Start a minimal HTTP/1 KV server.

    Endpoints (single-segment keys only):
      - GET /key
      - POST /key (body = value)
      - PUT /key  (body = value)
      - DELETE /key
    """

    items: dict[str, str] = {}

    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = FlowControlAsyncioStreamDriver(
            build_http_kv_channel(items),
            reader,
            writer,
            backpressure_sleep=0.001,
        )
        await drv.run()

    srv = await asyncio.start_server(_handle_client, host, port)
    async with srv:
        await srv.serve_forever()


def main() -> None:
    asyncio.run(serve_kv())


if __name__ == '__main__':
    main()
