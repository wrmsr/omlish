import asyncio
import dataclasses as dc
import types
import typing as ta

from omlish.http.headers import HttpHeaders  # noqa
from omlish.lite.check import check  # noqa
from omlish.lite.abstract import Abstract

from ....asyncs import AsyncChannelPipelineMessages  # noqa
from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ...requests import FullPipelineHttpRequest
from ...responses import FullPipelineHttpResponse  # noqa
from ...responses import PipelineHttpResponseHead  # noqa
from ...server.requests import PipelineHttpRequestBodyAggregator
from ...server.requests import PipelineHttpRequestHeadDecoder
from ...server.responses import PipelineHttpResponseEncoder


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class AsgiSpec:
    app: ta.Any
    host: str = '127.0.0.1'
    port: int = 8087


##


class _AsgiOp(Abstract):
    pass


@dc.dataclass(frozen=True)
class _ReceiveAsgiOp(_AsgiOp):
    pass


@dc.dataclass(frozen=True)
class _SendAsgiOp(_AsgiOp):
    msg: ta.Any


#


class _AsgiFutureNotAwaitedError(RuntimeError):
    pass


class _AsgiFuture(ta.Generic[T]):
    def __init__(self, arg: ta.Any) -> None:
        self.arg = arg

    done: bool = False
    result: T
    error: ta.Optional[BaseException] = None

    def __await__(self) -> ta.Generator['_AsgiFuture', None, T]:
        if not self.done:
            yield self
        if not self.done:
            raise _AsgiFutureNotAwaitedError
        if self.error is not None:
            raise self.error
        else:
            return self.result


#


class AsgiHandler(ChannelPipelineHandler):
    def __init__(self, app: ta.Any) -> None:
        super().__init__()

        self._app = app

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, FullPipelineHttpRequest):
            ctx.feed_in(msg)
            return

        #

        scope = {
            'asgi': {
                'spec_version': '2.3',
                'version': '3.0',
            },
            'client': ('127.0.0.1', 57782),
            'headers': [
                (b'host', b'localhost:8087'),
                (b'user-agent', b'curl/8.7.1'),
                (b'accept', b'*/*'),
            ],
            'http_version': '1.1',
            'method': 'GET',
            'path': '/ping',
            'query_string': b'',
            'raw_path': b'/ping',
            'root_path': '',
            'scheme': 'http',
            'server': ('127.0.0.1', 8087),
            'state': {},
            'type': 'http',
        }

        #

        @types.coroutine
        def receive() -> ta.Any:
            return _AsgiFuture(_ReceiveAsgiOp())

        @types.coroutine
        def send(asgi_msg: ta.Any) -> ta.Any:
            return _AsgiFuture(_SendAsgiOp(asgi_msg))

        #

        o = self._app(scope, receive, send)
        try:
            a = o.__await__()
            try:
                g = iter(a)
                try:
                    try:
                        f = g.send(None)  # noqa
                    except StopIteration as ex:
                        v = ex.value  # noqa

                    raise NotImplementedError

                finally:
                    # if g is not a:
                    #     self.ctx.run(g.close)
                    pass

            finally:
                # self.ctx.run(a.close)
                pass

        finally:
            # o.close()
            pass

        raise NotImplementedError


def build_asgi_channel(app: ta.Any) -> PipelineChannel.Spec:
    return PipelineChannel.Spec([
        PipelineHttpRequestHeadDecoder(),
        PipelineHttpRequestBodyAggregator(),
        PipelineHttpResponseEncoder(),
        AsgiHandler(app),
        FlatMapChannelPipelineHandlers.drop(
            'inbound',
            filter_type=(
                ChannelPipelineMessages.FinalInput,
                ChannelPipelineFlowMessages.FlushInput,
            ),
        ),
    ])


async def a_serve_asgi_pipeline(spec: AsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamPipelineChannelDriver(
            build_asgi_channel(spec.app),
            reader,
            writer,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, spec.host, spec.port)
    async with srv:
        await srv.serve_forever()


def serve_asgi_pipeline(spec: AsgiSpec) -> None:
    asyncio.run(a_serve_asgi_pipeline(spec))


##


def serve_asgi_uvicorn(spec: AsgiSpec) -> None:
    import uvicorn  # noqa

    server = uvicorn.Server(uvicorn.Config(
        spec.app,
        host=spec.host,
        port=spec.port,
    ))

    asyncio.run(server.serve())


##


async def ping_app(scope, receive, send):
    if scope['type'] != 'http':
        return

    method = scope.get('method')
    path = scope.get('path')

    if method == 'GET' and path == '/ping':
        body = b'pong'
        status = 200
    else:
        body = b'not found'
        status = 404

    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', b'text/plain'),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })


##


def _main() -> None:
    ping_spec = AsgiSpec(ping_app)

    # serve_asgi_uvicorn(ping_spec)
    serve_asgi_pipeline(ping_spec)


if __name__ == '__main__':
    _main()
