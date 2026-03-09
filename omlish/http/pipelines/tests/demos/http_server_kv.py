# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import typing as ta

from .....io.pipelines.asyncs import AsyncIoPipelineMessages
from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from .....io.pipelines.flow.stub import StubIoPipelineFlow
from .....io.streams.utils import ByteStreamBuffers
from .....logs.modules import get_module_loggers
from .....logs.std.standard import configure_standard_logging
from ...requests import FullIoPipelineHttpRequest
from ...server.requests import IoPipelineHttpRequestAggregatorDecoder
from ...server.requests import IoPipelineHttpRequestDecoder


log, alog = get_module_loggers(globals())


##


class KvStoreHandler(IoPipelineHandler):
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

    def __init__(self, items: ta.MutableMapping[str, str]) -> None:
        super().__init__()

        self._items = items

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, FullIoPipelineHttpRequest):
            ctx.feed_in(msg)
            return

        head = msg.head
        key = self._parse_key(head.target)
        if key is None:
            self._write_response(ctx, 400, b'bad request')
            ctx.feed_final_output()
            return

        method = head.method.upper()

        #

        aw = AsyncIoPipelineMessages.Await(alog.info(f'{method} {key}'))

        @aw.add_listener
        def after_log(_):
            pass

        ctx.feed_out(aw)

        #

        if method == 'GET':
            if key not in self._items:
                self._write_response(ctx, 404, b'not found')
            else:
                b = self._items[key].encode('utf-8')
                self._write_response(ctx, 200, b)
            ctx.feed_final_output()
            return

        if method in ('POST', 'PUT'):
            b = ByteStreamBuffers.to_bytes(msg.body)
            s = b.decode('utf-8', errors='replace')
            self._items[key] = s
            code = 201 if method == 'POST' else 200
            self._write_response(ctx, code, s.encode('utf-8'))
            ctx.feed_final_output()
            return

        if method == 'DELETE':
            if key not in self._items:
                self._write_response(ctx, 404, b'not found')
            else:
                del self._items[key]
                self._write_response(ctx, 200, b'deleted')
            ctx.feed_final_output()
            return

        self._write_response(ctx, 405, b'method not allowed')
        ctx.feed_final_output()

    def _parse_key(self, target: str) -> ta.Optional[str]:
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

    def _write_response(self, ctx: IoPipelineHandlerContext, status: int, body: bytes) -> None:
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


def build_http_kv_spec(
        items: ta.MutableMapping[str, str],
) -> IoPipeline.Spec:
    return IoPipeline.Spec(
        [
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpRequestAggregatorDecoder(),
            KvStoreHandler(items),
        ],
        services=[
            StubIoPipelineFlow(),
        ],
    )


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

    items: ta.Dict[str, str] = {}

    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamIoPipelineDriver(
            build_http_kv_spec(items),
            reader,
            writer,
            # backpressure_sleep=0.001,
        )
        await drv.run()

    srv = await asyncio.start_server(_handle_client, host, port)
    async with srv:
        await srv.serve_forever()


def main() -> None:
    configure_standard_logging()

    log.info('Server starting')

    asyncio.run(serve_kv())


if __name__ == '__main__':
    main()
