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
    def on_consumed(self, handler: 'ChannelPipelineHandler', cost: int) -> None:
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
            _pipeline: 'ChannelPipeline',
            _handler: 'ChannelPipelineHandler',
    ) -> None:
        super().__init__()

        self._pipeline = _pipeline
        self._handler = _handler

        self._handles_inbound = type(_handler).inbound is not ChannelPipelineHandler.inbound
        self._handles_outbound = type(_handler).outbound is not ChannelPipelineHandler.outbound

    _next_in: 'ChannelPipelineHandlerContext'  # 'next'
    _next_out: 'ChannelPipelineHandlerContext'  # 'prev'

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._handler!r}, {self.pipeline!r})'

    @property
    def pipeline(self) -> 'ChannelPipeline':
        return self._pipeline

    @property
    def channel(self) -> 'PipelineChannel':
        return self._pipeline._channel  # noqa

    @property
    def scheduler(self) -> ta.Optional['ChannelPipelineScheduler']:
        return self._pipeline._channel._scheduler  # noqa

    @property
    def handler(self) -> 'ChannelPipelineHandler':
        return self._handler

    #

    def feed_in(self, msg: ta.Any) -> None:
        nxt = self._next_in
        while not nxt._handles_inbound:  # noqa
            nxt = nxt._next_in  # noqa
        nxt._handler.inbound(nxt, msg)  # noqa

    def feed_out(self, msg: ta.Any) -> None:
        nxt = self._next_out  # noqa
        while not nxt._handles_outbound:  # noqa
            nxt = nxt._next_out  # noqa
        nxt._handler.outbound(nxt, msg)  # noqa

    def emit_out(self, msg: ta.Any) -> None:
        self._pipeline._channel.emit_out(msg)  # noqa

    #

    @property
    def bytes_flow_control(self) -> ta.Optional[BytesChannelPipelineFlowControl]:
        return self._pipeline._caches().find_handler(BytesChannelPipelineFlowControl)  # type: ignore[type-abstract]  # noqa


class ChannelPipelineHandler(Abstract):
    def added(self, ctx: ChannelPipelineHandlerContext) -> None:
        pass

    def removing(self, ctx: ChannelPipelineHandlerContext) -> None:
        pass

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_in(msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_out(msg)

    def scheduled(self, msg: ta.Any) -> None:
        raise NotImplementedError


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

        self._outermost = outermost = ChannelPipelineHandlerContext(
            _pipeline=self,
            _handler=ChannelPipeline._Outermost(),
        )
        self._innermost = innermost = ChannelPipelineHandlerContext(
            _pipeline=self,
            _handler=ChannelPipeline._Innermost(),
        )

        innermost._next_in = innermost._next_out = outermost  # noqa
        outermost._next_in = outermost._next_out = innermost  # noqa

        self._contexts: ta.Dict[ChannelPipelineHandler, ChannelPipelineHandlerContext] = {}

        for h in handlers:
            self.add_innermost(h)

    #

    def feed_in_from(self, handler: ChannelPipelineHandler, msg: ta.Any) -> None:
        ctx = self._contexts[handler]
        ctx._handler.inbound(ctx, msg)  # noqa

    def feed_out_from(self, handler: ChannelPipelineHandler, msg: ta.Any) -> None:
        ctx = self._contexts[handler]
        ctx._handler.outbound(ctx, msg)  # noqa

    #

    def _add(
            self,
            handler: ChannelPipelineHandler,
            *,
            inner_to: ta.Optional[ChannelPipelineHandlerContext] = None,
            outer_to: ta.Optional[ChannelPipelineHandlerContext] = None,
    ) -> None:
        if inner_to is not None:
            check.none(outer_to)
            check.is_not(inner_to, self._innermost)
        elif outer_to is not None:
            check.none(inner_to)
            check.is_not(outer_to, self._outermost)
        else:
            raise ValueError('Must specify exactly one of inner_to or outer_to')

        ctx = ChannelPipelineHandlerContext(
            _pipeline=self,
            _handler=handler,
        )

        self._contexts[handler] = ctx

        if inner_to is not None:
            prv = inner_to._next_in  # noqa
            ctx._next_out = inner_to  # noqa
            ctx._next_in = prv  # noqa
            inner_to._next_in = ctx  # noqa
            prv._next_out = ctx  # noqa

        if outer_to is not None:
            prv = outer_to._next_out  # noqa
            ctx._next_out = prv  # noqa
            ctx._next_in = outer_to  # noqa
            prv._next_in = ctx  # noqa
            outer_to._next_out = ctx  # noqa

        self._clear_caches()

        handler.added(ctx)

    def _remove(self, handler: ChannelPipelineHandler) -> None:
        ctx = self._contexts[handler]

        check.is_not(ctx, self._innermost)
        check.is_not(ctx, self._outermost)

        if (sched := self._channel._scheduler) is not None:  # noqa
            sched.cancel_all(handler)

        ctx.handler.removing(ctx)

        del self._contexts[handler]

        ctx._next_in._next_out = ctx._next_out  # noqa
        ctx._next_out._next_in = ctx._next_in  # noqa

        self._clear_caches()

    #

    def add_innermost(self, handler: ChannelPipelineHandler) -> None:
        self._add(handler, outer_to=self._innermost)

    def add_outermost(self, handler: ChannelPipelineHandler) -> None:
        self._add(handler, inner_to=self._outermost)

    #

    class _Outermost(ChannelPipelineHandler):
        def outbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            ctx.emit_out(msg)

    class _Innermost(ChannelPipelineHandler):
        def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            ctx.emit_out(msg)

    #

    class _Caches:
        def __init__(self, p: 'ChannelPipeline') -> None:
            self._p = p

            self._single_handlers_by_type_cache: ta.Dict[type, ta.Optional[ta.Any]] = {}
            self._handlers_by_type_cache: ta.Dict[type, ta.Sequence[ta.Any]] = {}

        def handlers(self) -> ta.Sequence[ChannelPipelineHandler]:
            lst: ta.List[ChannelPipelineHandler] = []
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                lst.append(ctx._handler)  # noqa
            return lst

        def find_handler(self, ty: ta.Type[T]) -> ta.Optional[T]:
            try:
                return self._single_handlers_by_type_cache[ty]
            except KeyError:
                pass

            self._single_handlers_by_type_cache[ty] = ret = check.opt_single(self.find_handlers(ty))
            return ret

        def find_handlers(self, ty: ta.Type[T]) -> ta.Sequence[T]:
            try:
                return self._handlers_by_type_cache[ty]
            except KeyError:
                pass

            self._handlers_by_type_cache[ty] = ret = [h for h in self._p._contexts if isinstance(h, ty)]  # noqa
            return ret

    __caches: _Caches

    def _caches(self) -> _Caches:
        try:
            return self.__caches
        except AttributeError:
            pass
        self.__caches = caches = ChannelPipeline._Caches(self)
        return caches

    def _clear_caches(self) -> None:
        try:
            del self.__caches
        except AttributeError:
            pass

    def handlers(self) -> ta.Sequence[ChannelPipelineHandler]:
        return self._caches().handlers()

    def find_handler(self, ty: ta.Type[T]) -> ta.Optional[T]:
        return self._caches().find_handler(ty)

    def find_handlers(self, ty: ta.Type[T]) -> ta.Sequence[T]:
        return self._caches().find_handlers(ty)


##


class ChannelPipelineScheduler(Abstract):
    class Handle(Abstract):
        @abc.abstractmethod
        def cancel(self) -> None:
            raise NotImplementedError

    @abc.abstractmethod
    def schedule(self, handler: ChannelPipelineHandler, msg: ta.Any) -> Handle:
        raise NotImplementedError

    @abc.abstractmethod
    def cancel_all(self, handler: ta.Optional[ChannelPipelineHandler] = None) -> None:
        raise NotImplementedError


##


@ta.final
class PipelineChannel:
    def __init__(
            self,
            handlers: ta.Sequence[ChannelPipelineHandler],
            *,
            scheduler: ta.Optional[ChannelPipelineScheduler] = None,
    ) -> None:
        super().__init__()

        self._scheduler = scheduler

        self._out_q: collections.deque[ta.Any] = collections.deque()

        self._saw_close = False
        self._saw_eof = False

        self._pipeline = ChannelPipeline(self, handlers)  # final

    @property
    def eof(self) -> bool:
        return self._saw_eof

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

        ctx = self._pipeline._outermost  # noqa
        try:
            ctx._handler.inbound(ctx, msg)  # noqa
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
        ctx = self._pipeline._innermost  # noqa
        try:
            ctx._handler.outbound(ctx, msg)  # noqa
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
