import abc
import typing as ta

from omlish import lang

from ..resources import ResourceManaged
from ..resources import Resources
from ..resources import ResourcesOption
from ..services import Response
from ..types import Option
from ..types import Output


O = ta.TypeVar('O')
O2 = ta.TypeVar('O2')
R = ta.TypeVar('R')
R2 = ta.TypeVar('R2')

V = ta.TypeVar('V')

OutputT = ta.TypeVar('OutputT', bound=Output)
StreamOutputT = ta.TypeVar('StreamOutputT', bound=Output)


##


class StreamOption(Option, lang.Abstract):
    pass


StreamOptions: ta.TypeAlias = StreamOption | ResourcesOption


##


class StreamResponseSink(lang.Abstract, ta.Generic[O]):
    @abc.abstractmethod
    def emit(self, item: O) -> ta.Awaitable[None]:
        raise NotImplementedError


class StreamResponseIterator(lang.Abstract, ta.Generic[O, R]):
    @abc.abstractmethod
    def __aenter__(self) -> ta.Awaitable[ta.Self]:
        raise NotImplementedError

    @abc.abstractmethod
    def __aexit__(self, exc_type, exc_val, exc_tb) -> ta.Awaitable[None]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def result(self) -> R:
        raise NotImplementedError

    @ta.final
    def __aiter__(self) -> ta.AsyncIterator[O]:
        return self

    @abc.abstractmethod
    def __anext__(self) -> ta.Awaitable[O]:
        raise NotImplementedError


##


class StreamServiceCancelledError(BaseException):
    pass


class StreamServiceNotAwaitedError(Exception):
    pass


class _StreamServiceResponse(StreamResponseIterator[O, R]):
    def __init__(
            self,
            fn: ta.Callable[[StreamResponseSink[O]], ta.Awaitable[R]],
    ) -> None:
        super().__init__()

        self._fn = fn

    @ta.final
    class _Emit(ta.Generic[O2]):
        def __init__(self, ssr: '_StreamServiceResponse', value: O2) -> None:
            self.ssr, self.value = ssr, value

        done: bool = False

        def __await__(self) -> ta.Generator['_StreamServiceResponse._Emit[O2]']:
            if not self.done:
                yield self
            if not self.done:
                raise StreamServiceNotAwaitedError

    @ta.final
    class _Sink(StreamResponseSink[O2]):
        def __init__(self, ssr: '_StreamServiceResponse[O2, R2]') -> None:
            super().__init__()

            self._ssr = ssr

        def emit(self, item: O2) -> ta.Awaitable[None]:
            return _StreamServiceResponse._Emit(self._ssr, item)

    _sink: _Sink[O]
    _a: ta.Any
    _cr: ta.Any

    async def __aenter__(self) -> ta.Self:
        self._sink = _StreamServiceResponse._Sink(self)
        self._cr = self._fn(self._sink)
        self._a = self._cr.__await__()
        self._g = iter(self._a)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not hasattr(self, '_result'):
            cex = StreamServiceCancelledError()
            try:
                self._g.throw(cex)
            except StreamServiceCancelledError as cex2:
                if cex2 is not cex:
                    raise
        if self._cr.cr_running:
            raise RuntimeError(f'Coroutine {self._cr!r} not terminated')
        if self._g is not self._a:
            self._g.close()
        self._a.close()
        self._cr.close()

    _result: R

    @property
    def result(self) -> R:
        return self._result

    async def __anext__(self) -> O:
        while True:
            try:
                x = self._g.send(None)
            except StopIteration as e:
                self._result = e.value
                raise StopAsyncIteration from None

            if isinstance(x, _StreamServiceResponse._Emit) and x.ssr is self:
                x.done = True
                return x.value

            await x


##


StreamResponse: ta.TypeAlias = Response[
    ResourceManaged[
        StreamResponseIterator[
            V,
            ta.Sequence[OutputT] | None,
        ],
    ],
    StreamOutputT,
]


async def new_stream_response(
        rs: Resources,
        fn: ta.Callable[[StreamResponseSink[V]], ta.Awaitable[ta.Sequence[OutputT] | None]],
        outputs: ta.Sequence[StreamOutputT] | None = None,
) -> StreamResponse[V, OutputT, StreamOutputT]:
    return StreamResponse(
        rs.new_managed(
            await rs.enter_async_context(
                _StreamServiceResponse(
                    fn,
                ),
            ),
        ),
        outputs or [],
    )
