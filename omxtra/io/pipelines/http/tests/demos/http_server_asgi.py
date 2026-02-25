# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import dataclasses as dc
import functools
import types
import typing as ta

from omlish.http.headers import HttpHeaders  # noqa
from omlish.lite.abstract import Abstract
from omlish.lite.check import check  # noqa

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


class _AsgiPump:
    def __init__(self, fn: ta.Any) -> None:
        super().__init__()

        self.fn = fn

    o: ta.Any
    a: ta.Any
    g: ta.Any

    def start(self) -> None:
        self.o = self.fn(self._receive, self._send)
        self.a = self.o.__await__()
        self.g = iter(self.a)

    def close(self) -> None:
        o = getattr(self, 'o', None)
        a = getattr(self, 'a', None)
        g = getattr(self, 'g', None)
        if g is not None and g is not a:
            g.close()
        if a is not None:
            a.close()
        if o is not None:
            o.close()

    @types.coroutine
    def _receive(self) -> ta.Any:
        return _AsgiFuture(_ReceiveAsgiOp())  # type: ignore

    @types.coroutine
    def _send(self, msg: ta.Any) -> ta.Any:
        return _AsgiFuture(_SendAsgiOp(msg))  # type: ignore


class _AsgiDriver:
    def __init__(self, fn: ta.Any) -> None:
        super().__init__()

        self._pump = _AsgiPump(fn)

    _state: ta.Literal[
        'new',

        'starting',
        'started',

        'response_started',
        'response_body_received',

        'closing',
        'closed',
    ] = 'new'

    def start(self) -> None:
        self._state = 'starting'
        self._pump.start()
        self._state = 'started'

    def close(self) -> None:
        if self._state in ('closing', 'closed'):
            return
        self._state = 'closing'
        self._pump.close()
        self._state = 'closed'

    class _Gv(ta.NamedTuple):
        k: ta.Literal['y', 'r']
        v: ta.Any

    def step(self) -> ta.Sequence[ta.Any]:
        if self._state == 'new':
            self.start()
        check.state(self._state == 'started')

        out: ta.List[ta.Any] = []

        while True:
            try:
                y = self._pump.g.send(None)  # noqa
            except StopIteration as si:
                r = si.value  # noqa
                check.not_isinstance(r, _AsgiFuture)
                gv = self._Gv('r', r)
            else:
                gv = self._Gv('y', y)

            if not self._step_one(gv, out):
                break

        return out

    #

    _response_start: ta.Optional[ta.Mapping[str, ta.Any]] = None
    _response_body: ta.Optional[ta.Mapping[str, ta.Any]] = None

    def _step_one(self, gv: _Gv, out: ta.List[ta.Any]) -> bool:
        if self._state == 'started':
            check.state(gv.k == 'y')
            f = check.isinstance(gv.v, _AsgiFuture)
            md = check.isinstance(check.isinstance(f.arg, _SendAsgiOp).msg, ta.Mapping)
            check.equal(md['type'], 'http.response.start')

            self._response_start = md
            self._state = 'response_started'

            f.result, f.done = None, True
            return True

        elif self._state == 'response_started':
            check.state(gv.k == 'y')
            f = check.isinstance(gv.v, _AsgiFuture)
            md = check.isinstance(check.isinstance(f.arg, _SendAsgiOp).msg, ta.Mapping)
            check.equal(md['type'], 'http.response.body')

            if md.get('more_body', False):
                raise NotImplementedError  # noqa

            self._response_body = md
            self._state = 'response_body_received'

            f.result, f.done = None, True
            return True

        elif self._state == 'response_body_received':
            check.state(gv.k == 'r')
            check.state(gv.v is None)

            resp = self._build_response()
            out.append(resp)

            out.append(ChannelPipelineMessages.FinalOutput())

            self.close()
            return False

        else:
            raise RuntimeError(f'Invalid state: {self._state!r}')

    def _build_response(self) -> FullPipelineHttpResponse:
        check.state(self._state == 'response_body_received')

        rs = check.not_none(self._response_start)
        rb = check.not_none(self._response_body)

        return FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                status=(status_code := rs['status']),
                reason=PipelineHttpResponseHead.get_reason_phrase(status_code),
                headers=HttpHeaders(rs['headers']),
            ),
            body=rb['body'],
        )


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
            # 'client': ('127.0.0.1', 57782),
            'headers': [
                (k.encode(), v.encode())
                for k, v in msg.head.headers.all
            ],
            'http_version': '1.1',
            'method': msg.head.method,
            'path': msg.head.target,
            # 'query_string': b'',
            # 'raw_path': b'/ping',
            # 'root_path': '',
            'scheme': 'http',
            # 'server': ('127.0.0.1', 8087),
            'state': {},
            'type': 'http',
        }

        #

        drv = _AsgiDriver(functools.partial(self._app, scope))

        out_msgs = drv.step()
        for out_msg in out_msgs:
            ctx.feed_out(out_msg)


def build_asgi_channel(app: ta.Any) -> PipelineChannel.Spec:
    return PipelineChannel.Spec(
        [
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
        ],
    )


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
