# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import collections
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check


T = ta.TypeVar('T')


##


class ChannelPipelineEvents:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @ta.final
    @dc.dataclass(frozen=True)
    class Eof:
        """Signals that the inbound byte stream reached EOF."""

    @ta.final
    @dc.dataclass(frozen=True)
    class Close:
        """Requests that the channel/pipeline close."""

    @ta.final
    @dc.dataclass(frozen=True)
    class Error:
        """Signals an exception occurred in the pipeline."""

        exc: BaseException


class ChannelPipelineError(Exception):
    pass


class ChannelPipelineContextInvalidatedError(ChannelPipelineError):
    pass


##


class ChannelPipelineFlowControl(Abstract):
    """
    Present in core largely just to work around mypy `type-abstract` errors (see https://peps.python.org/pep-0747/ ),
    but also for the 'special cased' bytes case below.

    ChannelPipelines as a concept and core mechanism are useful independent of the notion of 'bytes', and the core
    machinery is generally kept pure and generic (including the flow control machinery). In practice though their main
    usecase *is* bytes in / bytes out, and as such it has this tiny bit of special-cased support in the core. But again,
    it's really only due to the current `type-abstract` deficiency of mypy.

    Aside from the special BytesChannelPipelineFlowControl case, there may be any number of flow control handlers in a
    pipeline - other handlers can choose to find and talk to them as they wish.
    """

    @abc.abstractmethod
    def get_cost(self, msg: ta.Any) -> ta.Optional[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def on_consumed(self, cost: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def want_read(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def drain_outbound(self, max_cost: ta.Optional[int] = None) -> ta.List[ta.Any]:
        raise NotImplementedError


class BytesChannelPipelineFlowControl(ChannelPipelineFlowControl, Abstract):
    """
    Special cased flow control specifically for 'external' bytes streams. Many of the decoders will talk to the instance
    of this (if present) to report the bytes they've consumed as they consume them. If present in a pipeline it must be
    unique, and should generally be at the outermost position.
    """


##


@ta.final
class ChannelPipelineHandlerContext:
    def __init__(
            self,
            *,
            _state: 'ChannelPipeline._State',  # noqa
            _index: int,
            _handler: 'ChannelPipelineHandler',
    ) -> None:
        super().__init__()

        self._state = _state
        self._index = _index
        self._handler = _handler

        self._next_in_index = _state.next_in_indexes[_index]
        self._next_out_index = _state.next_out_indexes[_index]

    def __repr__(self) -> str:
        return f'{type(self).__name__}<{self._index}>({self._handler!r}, {self.pipeline!r})'

    @property
    def pipeline(self) -> 'ChannelPipeline':
        return self._state.pipeline

    @property
    def channel(self) -> 'PipelineChannel':
        return self._state.pipeline._channel  # noqa

    @property
    def index(self) -> int:
        return self._index

    @property
    def handler(self) -> 'ChannelPipelineHandler':
        return self._handler

    @property
    def invalidated(self) -> bool:
        return self._state.invalidated

    #

    def feed_in(self, msg: ta.Any) -> None:
        self._state.feed_in_from(self._next_in_index, msg)

    def feed_out(self, msg: ta.Any) -> None:
        self._state.feed_out_from(self._next_out_index, msg)

    def emit_out(self, msg: ta.Any) -> None:
        self._state.pipeline._channel.emit_out(msg)  # noqa

    #

    def get_handler(self, ty: ta.Type[T]) -> ta.Optional[T]:
        return self._state.get_handler(ty)

    def get_handlers(self, ty: ta.Type[T]) -> ta.Sequence[T]:
        return self._state.get_handlers(ty)

    #

    @property
    def bytes_flow_control(self) -> ta.Optional[BytesChannelPipelineFlowControl]:
        return self._state.get_handler(BytesChannelPipelineFlowControl)  # type: ignore[type-abstract]


class ChannelPipelineHandler(Abstract):
    def handler_added(self, ctx: ChannelPipelineHandlerContext) -> None:
        pass

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_in(msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_out(msg)


##


@ta.final
class ChannelPipeline:
    def __init__(
            self,
            channel: 'PipelineChannel',
            handlers: ta.Sequence[ChannelPipelineHandler],
    ) -> None:
        super().__init__()

        self._channel = channel  # final

        self.__state = st = self.__new_state([
            ChannelPipeline._Outermost(),
            *handlers,
            ChannelPipeline._Innermost(),
        ])

        for ctx in st.ctxs:
            ctx.handler.handler_added(ctx)

    @ta.final
    class _State:
        def __init__(
                self,
                pipeline: 'ChannelPipeline',
                handlers: ta.Sequence[ChannelPipelineHandler],
        ) -> None:
            self.pipeline = pipeline
            self.handlers = check.not_empty(handlers)

            check.isinstance(handlers[0], ChannelPipeline._Outermost)
            check.isinstance(handlers[-1], ChannelPipeline._Innermost)

            self.invalidated = False

            self.next_in_indexes, self.next_out_indexes = self._calculate_link_lists(handlers)

            self.ctxs = [
                ChannelPipelineHandlerContext(
                    _state=self,
                    _index=i,
                    _handler=h,
                )
                for i, h in enumerate(handlers)
            ]

            self._single_handlers_by_type_cache: ta.Dict[type, ta.Optional[ta.Any]] = {}
            self._handlers_by_type_cache: ta.Dict[type, ta.Sequence[ta.Any]] = {}

            # The result of this is discarded - this is done to enforce uniqueness of this special cased handler if it's
            # present.
            self.get_handler(BytesChannelPipelineFlowControl)  # type: ignore[type-abstract]

        #

        @classmethod
        def _calculate_link_lists(
                cls,
                handlers: ta.Sequence[ChannelPipelineHandler],
        ) -> ta.Tuple[ta.Sequence[int], ta.Sequence[int]]:
            n = len(handlers)

            next_in_indexes = [-1] * n
            next_out_indexes = [-1] * n

            last_in = -1
            for i in range(n - 1, -1, -1):
                next_in_indexes[i] = last_in
                if type(handlers[i]).inbound is not ChannelPipelineHandler.inbound or i == n - 1:
                    last_in = i

            last_out = -1
            for i in range(n):
                next_out_indexes[i] = last_out
                if type(handlers[i]).outbound is not ChannelPipelineHandler.outbound or i == 0:
                    last_out = i

            return next_in_indexes, next_out_indexes

        #

        def check_invalidated(self) -> None:
            if self.invalidated:
                raise ChannelPipelineContextInvalidatedError

        #

        def get_handler(self, ty: ta.Type[T]) -> ta.Optional[T]:
            try:
                return self._single_handlers_by_type_cache[ty]
            except KeyError:
                pass

            self._single_handlers_by_type_cache[ty] = ret = check.opt_single(self.get_handlers(ty))
            return ret

        def get_handlers(self, ty: ta.Type[T]) -> ta.Sequence[T]:
            try:
                return self._handlers_by_type_cache[ty]
            except KeyError:
                pass

            self._handlers_by_type_cache[ty] = ret = [h for h in self.handlers if isinstance(h, ty)]
            return ret

        #

        def feed_in_from(self, idx: int, msg: ta.Any) -> None:
            if self.invalidated:
                raise ChannelPipelineContextInvalidatedError
            if idx < 0:
                raise RuntimeError(f'Negative handler index {idx!r}.')
            ctx = self.ctxs[idx]
            ctx._handler.inbound(ctx, msg)  # noqa

        def feed_out_from(self, idx: int, msg: ta.Any) -> None:
            if self.invalidated:
                raise ChannelPipelineContextInvalidatedError
            if idx < 0:
                raise RuntimeError(f'Negative handler index {idx!r}.')
            ctx = self.ctxs[idx]
            ctx._handler.outbound(ctx, msg)  # noqa

    def __new_state(self, handlers: ta.Sequence[ChannelPipelineHandler]) -> _State:
        return self._State(self, handlers)

    __state: _State

    def _state(self) -> _State:
        return self.__state

    #

    def get_handler(self, ty: ta.Type[T]) -> ta.Optional[T]:
        return self._state().get_handler(ty)

    def get_handlers(self, ty: ta.Type[T]) -> ta.Sequence[T]:
        return self._state().get_handlers(ty)

    #

    class _Outermost(ChannelPipelineHandler):
        def outbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            ctx.emit_out(msg)

    class _Innermost(ChannelPipelineHandler):
        def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            ctx.emit_out(msg)


##


@ta.final
class PipelineChannel:
    def __init__(
            self,
            handlers: ta.Sequence[ChannelPipelineHandler],
    ) -> None:
        super().__init__()

        self._out_q: collections.deque[ta.Any] = collections.deque()

        self._saw_close = False
        self._saw_eof = False

        self._pipeline = ChannelPipeline(self, handlers)  # final

    @property
    def closed(self) -> bool:
        return self._saw_close

    @property
    def pipeline(self) -> ChannelPipeline:
        return self._pipeline

    #

    def _feed_in(self, msg: ta.Any) -> None:
        if self._saw_close or self._saw_eof:
            return

        if isinstance(msg, ChannelPipelineEvents.Eof):
            self._saw_eof = True

        if isinstance(msg, ChannelPipelineEvents.Close):
            self._saw_close = True

        st = self._pipeline._state()  # noqa
        try:
            st.feed_in_from(1, msg)  # Skip outermost
        except BaseException as e:  # noqa
            self.handle_error(e)

    def feed_in(self, msg: ta.Any) -> None:
        self._feed_in(msg)

    def feed_eof(self) -> None:
        if self._saw_close or self._saw_eof:
            return

        self._feed_in(ChannelPipelineEvents.Eof())

    def feed_close(self) -> None:
        if self._saw_close:
            return

        self._feed_in(ChannelPipelineEvents.Close())

    #

    def feed_out(self, msg: ta.Any) -> None:
        st = self._pipeline._state()  # noqa
        try:
            st.feed_out_from(len(st.ctxs) - 2, msg)  # Skip innermost
        except BaseException as e:  # noqa
            self.handle_error(e)

    #

    def emit_out(self, msg: ta.Any) -> None:
        self._out_q.append(msg)

    def poll_out(self) -> ta.Optional[ta.Any]:
        if not self._out_q:
            return None

        return self._out_q.popleft()

    def drain_out(self) -> ta.List[ta.Any]:
        out: ta.List[ta.Any] = []

        while self._out_q:
            out.append(self._out_q.popleft())

        return out

    #

    def handle_error(self, e: BaseException) -> None:
        self.emit_out(ChannelPipelineEvents.Error(e))

        self.feed_close()
