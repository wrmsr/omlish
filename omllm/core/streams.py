import abc
import itertools
import types
import typing as ta

from omcore import check
from omcore import lang
from omcore import resources as rs


EV = ta.TypeVar('EV')
RV = ta.TypeVar('RV')
EV2 = ta.TypeVar('EV2')
V = ta.TypeVar('V')


##


class StreamSink(lang.Abstract, ta.Generic[EV]):
    @abc.abstractmethod
    def emit(self, value: EV) -> ta.Awaitable[None]:
        raise NotImplementedError


class StreamIterator(
    ta.AsyncContextManager['StreamIterator[EV, RV]'],
    lang.Abstract,
    ta.Generic[EV, RV],
):
    @property
    @abc.abstractmethod
    def result(self) -> lang.Maybe[RV]:
        raise NotImplementedError

    @ta.final
    def __aiter__(self) -> ta.AsyncIterator[EV]:
        return self

    @abc.abstractmethod
    def __anext__(self) -> ta.Awaitable[EV]:
        raise NotImplementedError


##


class StreamCancelledError(BaseException):
    pass


class StreamNotAwaitedError(Exception):
    pass


class _Stream(StreamIterator[EV, RV]):
    def __init__(
            self,
            fn: ta.Callable[[StreamSink[EV]], ta.Awaitable[RV]],
    ) -> None:
        super().__init__()

        self._fn = fn

    @ta.final
    class _Emit(ta.Generic[EV2]):
        def __init__(self, ssr: _Stream, value: EV2) -> None:
            self.ssr, self.value = ssr, value

        done: bool = False

        def __await__(self) -> ta.Generator[_Stream._Emit[EV2]]:
            if not self.done:
                yield self
            if not self.done:
                raise StreamNotAwaitedError

    @ta.final
    class _Sink(StreamSink[EV2]):
        def __init__(self, ssr: _Stream) -> None:
            super().__init__()

            self._ssr = ssr

        def emit(self, item: EV2) -> ta.Awaitable[None]:
            return _Stream._Emit(self._ssr, item)

    _state: ta.Literal['new', 'running', 'closed'] = 'new'

    _sink: _Sink[EV]

    _cr: ta.Any
    _a: ta.Any
    _g: ta.Any

    async def __aenter__(self) -> ta.Self:
        check.state(self._state == 'new')
        self._state = 'running'

        self._sink = _Stream._Sink(self)

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
            cex = StreamCancelledError()

            i = None
            for n in itertools.count():
                try:
                    if not n:
                        x = self._g.throw(cex)
                    else:
                        x = self._g.send(i)

                except StreamCancelledError as cex2:
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

    _result: lang.Maybe[RV] = lang.empty()

    @property
    def result(self) -> lang.Maybe[RV]:
        return self._result

    @types.coroutine
    def _anext(self):
        check.state(self._state == 'running')

        i = None
        while True:
            try:
                x = self._g.send(i)

            except StopIteration as e:
                self._result = lang.just(e.value)

                raise StopAsyncIteration from None

            if isinstance(x, _Stream._Emit) and x.ssr is self:
                check.state(not x.done)
                x.done = True
                return x.value

            i = yield x

    async def __anext__(self) -> EV:
        return await self._anext()


##


type Stream[EV, RV] = rs.AsyncResourceManaged[StreamIterator[EV, RV]]


async def new_stream(
        fn: ta.Callable[[StreamSink[EV]], ta.Awaitable[RV]],
) -> Stream[EV, RV]:
    async with await rs.async_contextual_or_new() as rm:
        ssr = _Stream(fn)

        return rm.new_managed(await rm.enter_async_context(ssr))
