"""
TODO:
 - new_stream_response carry TypeAlias __orig_type__ somehow
"""
import abc
import itertools
import types
import typing as ta

from omlish import check
from omlish import lang

from ..resources import ResourceManaged
from ..resources import Resources
from ..resources import ResourcesOption
from ..services.responses import Response
from ..services.responses import ResponseMetadatas
from ..types import Option
from ..types import Output


EV = ta.TypeVar('EV')
RV = ta.TypeVar('RV')

EV2 = ta.TypeVar('EV2')

V = ta.TypeVar('V')

OutputT = ta.TypeVar('OutputT', bound=Output)


##


class StreamOption(Option, lang.Abstract):
    pass


StreamOptions: ta.TypeAlias = StreamOption | ResourcesOption


##


class StreamResponseSink(lang.Abstract, ta.Generic[EV]):
    @abc.abstractmethod
    def emit(self, value: EV) -> ta.Awaitable[None]:
        raise NotImplementedError


class StreamResponseIterator(
    ta.AsyncContextManager['StreamResponseIterator[EV, RV]'],
    lang.Abstract,
    ta.Generic[EV, RV],
):
    @property
    @abc.abstractmethod
    def returned(self) -> lang.Maybe[RV]:
        raise NotImplementedError

    @ta.final
    def __aiter__(self) -> ta.AsyncIterator[EV]:
        return self

    @abc.abstractmethod
    def __anext__(self) -> ta.Awaitable[EV]:
        raise NotImplementedError


##


class StreamServiceCancelledError(BaseException):
    pass


class StreamServiceNotAwaitedError(Exception):
    pass


class _StreamServiceResponse(StreamResponseIterator[EV, RV]):
    def __init__(
            self,
            fn: ta.Callable[[StreamResponseSink[EV]], ta.Awaitable[RV]],
    ) -> None:
        super().__init__()

        self._fn = fn

    @ta.final
    class _Emit(ta.Generic[EV2]):
        def __init__(self, ssr: _StreamServiceResponse, value: EV2) -> None:
            self.ssr, self.value = ssr, value

        done: bool = False

        def __await__(self) -> ta.Generator[_StreamServiceResponse._Emit[EV2]]:
            if not self.done:
                yield self
            if not self.done:
                raise StreamServiceNotAwaitedError

    @ta.final
    class _Sink(StreamResponseSink[EV2]):
        def __init__(self, ssr: _StreamServiceResponse) -> None:
            super().__init__()

            self._ssr = ssr

        def emit(self, item: EV2) -> ta.Awaitable[None]:
            return _StreamServiceResponse._Emit(self._ssr, item)

    _state: ta.Literal['new', 'running', 'closed'] = 'new'

    _sink: _Sink[EV]

    _cr: ta.Any
    _a: ta.Any
    _g: ta.Any

    async def __aenter__(self) -> ta.Self:
        check.state(self._state == 'new')
        self._state = 'running'

        self._sink = _StreamServiceResponse._Sink(self)

        self._cr = self._fn(self._sink)
        self._a = self._cr.__await__()
        self._g = iter(self._a)

        return self

    @types.coroutine
    def _aexit(self, exc_type, exc_val, exc_tb):
        old_state = self._state
        self._state = 'closed'
        if old_state != 'running':
            return

        if self._cr.cr_running or self._cr.cr_suspended:
            cex = StreamServiceCancelledError()

            i = None
            for n in itertools.count():
                try:
                    if not n:
                        x = self._g.throw(cex)
                    else:
                        x = self._g.send(i)

                except StreamServiceCancelledError as cex2:
                    if cex2 is cex:
                        break

                    raise

                i = yield x

        if self._cr.cr_running:
            raise RuntimeError(f'Coroutine {self._cr!r} not terminated')

        if self._g is not self._a:
            self._g.close()
        self._a.close()
        self._cr.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._aexit(exc_type, exc_val, exc_tb)

    _returned: lang.Maybe[RV] = lang.empty()

    @property
    def returned(self) -> lang.Maybe[RV]:
        return self._returned

    @types.coroutine
    def _anext(self):
        check.state(self._state == 'running')

        i = None
        while True:
            try:
                x = self._g.send(i)

            except StopIteration as e:
                self._returned = lang.just(e.value)

                raise StopAsyncIteration from None

            if isinstance(x, _StreamServiceResponse._Emit) and x.ssr is self:
                check.state(not x.done)
                x.done = True
                return x.value

            i = yield x

    async def __anext__(self) -> EV:
        return await self._anext()


##


StreamResponse: ta.TypeAlias = Response[ResourceManaged[StreamResponseIterator[EV, RV]], OutputT]


async def new_stream_response(
        rs: Resources,
        fn: ta.Callable[[StreamResponseSink[EV]], ta.Awaitable[RV]],
        outputs: ta.Sequence[OutputT] | None = None,
        *,
        metadata: ta.Sequence[ResponseMetadatas] | None = None,
) -> StreamResponse[EV, RV, OutputT]:
    ssr = _StreamServiceResponse(fn)

    v = rs.new_managed(await rs.enter_async_context(ssr))

    try:
        sr = StreamResponse(v, outputs or [])
        if metadata:
            sr = sr.with_metadata(*metadata)
        return sr

    except BaseException:  # noqa
        # The StreamResponse ctor can raise - for example in `_tv_field_coercer` - in which case we need to clean up the
        # resources ref we have already allocated before reraising.
        async with v:
            pass

        raise
