# ruff: noqa: UP006 UP045
# @omlish-lite
import collections.abc
import dataclasses as dc
import enum
import functools
import types
import typing as ta

from .....io.pipelines.asyncs import AsyncIoPipelineMessages
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.flow.types import IoPipelineFlow
from .....lite.abstract import Abstract
from .....lite.check import check
from ....headers import HttpHeaders
from ...requests import FullIoPipelineHttpRequest
from ...responses import IoPipelineHttpResponseHead


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
    def __init__(self, ctx: IoPipelineHandlerContext, fn: ta.Any) -> None:
        super().__init__()

        self._ctx = ctx
        self._pump = _AsgiPump(fn)

    #

    class State(enum.Enum):
        NEW = 'new'

        STARTING = 'starting'
        RUNNING = 'running'
        RECEIVING = 'receiving'

        RESPONSE_STARTED = 'response_started'
        RESPONSE_FINISHED = 'response_finished'

        CLOSING = 'closing'
        CLOSED = 'closed'

    _state: State = State.NEW

    @property
    def state(self) -> State:
        return self._state

    #

    def start(self) -> None:
        self._state = _AsgiDriver.State.NEW
        self._pump.start()
        self._state = _AsgiDriver.State.RUNNING

    def close(self) -> None:
        if self._state in (_AsgiDriver.State.CLOSING, _AsgiDriver.State.CLOSED):
            return
        self._state = _AsgiDriver.State.CLOSING
        self._pump.close()
        self._state = _AsgiDriver.State.CLOSED

    #

    class _Gv(ta.NamedTuple):
        k: ta.Literal['y', 'r']
        v: ta.Any

    def step(self) -> None:
        if self._state == _AsgiDriver.State.NEW:
            self.start()
        check.state(self._state not in (
            _AsgiDriver.State.NEW,
            _AsgiDriver.State.STARTING,
            _AsgiDriver.State.CLOSING,
            _AsgiDriver.State.CLOSED,
        ))

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

        for out_msg in out:
            self._ctx.feed_out(out_msg)

    #

    _receiving_fut: ta.Optional[_AsgiFuture] = None

    def _step_one(self, gv: _Gv, out: ta.List[ta.Any]) -> bool:
        if gv.k == 'y' and not isinstance(gv.v, _AsgiFuture):
            awm = AsyncIoPipelineMessages.Await(gv.v)
            awm.add_listener(lambda _: self.step())
            out.append(awm)
            return False

        if self._state == _AsgiDriver.State.RUNNING:
            check.state(gv.k == 'y')
            f = check.isinstance(gv.v, _AsgiFuture)

            if isinstance(f.arg, _SendAsgiOp):
                md = check.isinstance(f.arg.msg, collections.abc.Mapping)
                check.equal(md['type'], 'http.response.start')

                out.append(IoPipelineHttpResponseHead(
                    status=(status_code := md['status']),
                    reason=IoPipelineHttpResponseHead.get_reason_phrase(status_code),
                    headers=HttpHeaders(md['headers']),
                ))
                IoPipelineFlow.maybe_flush_output(self._ctx)

                self._state = _AsgiDriver.State.RESPONSE_STARTED

                f.result, f.done = None, True
                return True

            elif isinstance(f.arg, _ReceiveAsgiOp):
                check.none(self._receiving_fut)
                self._receiving_fut = f

                IoPipelineFlow.maybe_ready_for_input(self._ctx)

                self._state = _AsgiDriver.State.RECEIVING

                return False

            else:
                raise TypeError(f.arg)

        elif self._state == _AsgiDriver.State.RESPONSE_STARTED:
            check.state(gv.k == 'y')
            f = check.isinstance(gv.v, _AsgiFuture)
            md = check.isinstance(check.isinstance(f.arg, _SendAsgiOp).msg, collections.abc.Mapping)
            check.equal(md['type'], 'http.response.body')

            out.append(md['body'])
            IoPipelineFlow.maybe_flush_output(self._ctx)

            if not md.get('more_body', False):
                self._state = _AsgiDriver.State.RESPONSE_FINISHED

            f.result, f.done = None, True
            return True

        elif self._state == _AsgiDriver.State.RESPONSE_FINISHED:
            check.state(gv.k == 'r')
            check.state(gv.v is None)

            out.append(IoPipelineMessages.FinalOutput())

            self.close()
            return False

        else:
            raise RuntimeError(f'Invalid state: {self._state!r}')


#


class AsgiHandler(IoPipelineHandler):
    def __init__(self, app: ta.Any) -> None:
        super().__init__()

        self._app = app

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            IoPipelineFlow.maybe_ready_for_input(ctx)

            return

        if not isinstance(msg, FullIoPipelineHttpRequest):
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

        drv = _AsgiDriver(ctx, functools.partial(self._app, scope))

        drv.step()

        check.state(drv.state == _AsgiDriver.State.CLOSED)
