# ruff: noqa: UP006 UP045
# @omlish-lite
"""
TODO:
 - re-add BytesChannelPipelineFlowControl unique check (without thrashing cache)?
 - 'optional' / 'advisory' event abstract base class? if any non-this isn't 'handled' by some 'driver', raise
   - need to catch stray bytes falling out
"""
import abc
import collections
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.namespaces import NamespaceClass

from .errors import ClosedChannelPipelineError
from .errors import ContextInvalidatedChannelPipelineError
from .errors import MessageNotPropagatedChannelPipelineError
from .errors import SawEofChannelPipelineError


T = ta.TypeVar('T')


##


class ChannelPipelineMessages(NamespaceClass):
    """Standard messages sent through a channel pipeline."""

    class NeverInbound(Abstract):
        pass

    class NeverOutbound(Abstract):
        pass

    class MustPropagate(Abstract):
        """
        These must be propagated all the way through the pipeline when sent in either direction. This is enforced via
        object identity - the same *instance* of the message must be seen at the end of the pipeline to be considered
        caught. This is intentional.
        """

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class Eof(NeverOutbound, MustPropagate):
        """Signals that the inbound stream reached EOF."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}@{id(self):x}()'

    @ta.final
    @dc.dataclass(frozen=True)
    class Close(NeverInbound, MustPropagate):
        """Requests that the channel/pipeline close."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}@{id(self):x}()'


##


class ChannelPipelineEvents(NamespaceClass):
    """Standard events emitted from a channel pipeline."""

    @ta.final
    @dc.dataclass(frozen=True)
    class Error:
        """Signals an exception occurred in the pipeline."""

        exc: BaseException


class ChannelPipelineError(Exception):
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
    """
    Passed to ChannelPipelineHandler methods, provides handler-specific access and operations the pipeline channel.

    Instances of this are never to be cached or shared - they are only considered valid within the scope of a single
    handler method call.
    """

    def __init__(
            self,
            *,
            _pipeline: 'ChannelPipeline',
            _handler: 'ChannelPipelineHandler',
    ) -> None:
        super().__init__()

        self._pipeline: ta.Final[ChannelPipeline] = _pipeline
        self._handler: ta.Final[ChannelPipelineHandler] = _handler

        self._handles_inbound = type(_handler).inbound is not ChannelPipelineHandler.inbound
        self._handles_outbound = type(_handler).outbound is not ChannelPipelineHandler.outbound

    _next_in: 'ChannelPipelineHandlerContext'  # 'next'
    _next_out: 'ChannelPipelineHandlerContext'  # 'prev'

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}@{id(self):x}'
            f'{"<INVALIDATED>" if self._invalidated else ""}'
            f'({self._handler!r}, {self.pipeline!r})'
        )

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

    _invalidated = False

    @property
    def invalidated(self) -> bool:
        return self._invalidated

    #

    def _inbound(self, msg: ta.Any) -> None:
        if self._invalidated:
            raise ContextInvalidatedChannelPipelineError
        check.not_isinstance(msg, ChannelPipelineMessages.NeverInbound)

        if isinstance(msg, ChannelPipelineMessages.MustPropagate):
            self._pipeline._channel._add_must_propagate('inbound', msg)  # noqa

        self._handler.inbound(self, msg)

    def _outbound(self, msg: ta.Any) -> None:
        if self._invalidated:
            raise ContextInvalidatedChannelPipelineError
        check.not_isinstance(msg, ChannelPipelineMessages.NeverOutbound)

        if isinstance(msg, ChannelPipelineMessages.MustPropagate):
            self._pipeline._channel._add_must_propagate('outbound', msg)  # noqa

        self._handler.outbound(self, msg)

    #

    def feed_in(self, msg: ta.Any) -> None:
        nxt = self._next_in
        while not nxt._handles_inbound:  # noqa
            nxt = nxt._next_in  # noqa
        nxt._inbound(msg)  # noqa

    def feed_out(self, msg: ta.Any) -> None:
        nxt = self._next_out  # noqa
        while not nxt._handles_outbound:  # noqa
            nxt = nxt._next_out  # noqa
        nxt._outbound(msg)  # noqa

    def emit(self, msg: ta.Any) -> None:
        self._pipeline._channel.emit(msg)  # noqa

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

    def scheduled(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        raise NotImplementedError


##


@ta.final
class ChannelPipeline:
    def __init__(
            self,
            channel: 'PipelineChannel',
            handlers: ta.Sequence[ChannelPipelineHandler] = (),
    ) -> None:
        super().__init__()

        self._channel: ta.Final[PipelineChannel] = channel

        self._outermost = outermost = ChannelPipelineHandlerContext(
            _pipeline=self,
            _handler=ChannelPipeline._Outermost(),
        )
        self._innermost = innermost = ChannelPipelineHandlerContext(
            _pipeline=self,
            _handler=ChannelPipeline._Innermost(),
        )

        # Explicitly does not form a ring, iteration past the outermost/innermost is always an error and will
        # intentionally raise AttributeError if not caught earlier.
        outermost._next_in = innermost  # noqa
        innermost._next_out = outermost  # noqa

        self._contexts: ta.Final[ta.Dict[ChannelPipelineHandler, ChannelPipelineHandlerContext]] = {}

        for h in handlers:
            self.add_innermost(h)

    _outermost: ta.Final[ChannelPipelineHandlerContext]
    _innermost: ta.Final[ChannelPipelineHandlerContext]

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}()'

    #

    def feed_in_to(self, handler: ChannelPipelineHandler, msg: ta.Any) -> None:
        ctx = self._contexts[handler]
        ctx._inbound(msg)  # noqa

    def feed_out_to(self, handler: ChannelPipelineHandler, msg: ta.Any) -> None:
        ctx = self._contexts[handler]
        ctx._outbound(msg)  # noqa

    #

    def _check_can_add(self, handler: ChannelPipelineHandler) -> ChannelPipelineHandler:
        check.not_in(handler, self._contexts)

        return handler

    def _add(
            self,
            handler: ChannelPipelineHandler,
            *,
            inner_to: ta.Optional[ChannelPipelineHandlerContext] = None,
            outer_to: ta.Optional[ChannelPipelineHandlerContext] = None,
    ) -> None:
        self._check_can_add(handler)

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

    def _check_can_remove(self, handler: ChannelPipelineHandler) -> ChannelPipelineHandler:
        ctx = self._contexts[handler]

        check.is_not(ctx, self._innermost)
        check.is_not(ctx, self._outermost)

        return handler

    def _remove(self, handler: ChannelPipelineHandler) -> None:
        self._check_can_remove(handler)

        ctx = self._contexts[handler]

        self._channel._removing(handler)  # noqa

        handler.removing(ctx)

        del self._contexts[handler]

        ctx._next_in._next_out = ctx._next_out  # noqa
        ctx._next_out._next_in = ctx._next_in  # noqa

        ctx._invalidated = True  # noqa
        del ctx._next_in  # noqa
        del ctx._next_out  # noqa

        self._clear_caches()

    #

    def add_innermost(self, handler: ChannelPipelineHandler) -> None:
        self._add(handler, outer_to=self._innermost)

    def add_outermost(self, handler: ChannelPipelineHandler) -> None:
        self._add(handler, inner_to=self._outermost)

    def remove(self, handler: ChannelPipelineHandler) -> None:
        self._remove(handler)

    def replace(self, old_handler: ChannelPipelineHandler, new_handler: ChannelPipelineHandler) -> None:
        self._check_can_remove(old_handler)
        self._check_can_add(new_handler)

        inner_to = self._contexts[old_handler]._next_out  # noqa
        self._remove(old_handler)
        self._add(new_handler, inner_to=inner_to)

    #

    class _Outermost(ChannelPipelineHandler):
        """'Head' in netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def outbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._remove_must_propagate('outbound', msg)  # noqa

            ctx.emit(msg)

    class _Innermost(ChannelPipelineHandler):
        """'Tail' in netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._remove_must_propagate('inbound', msg)  # noqa

            ctx.emit(msg)

    #

    class _Caches:
        def __init__(self, p: 'ChannelPipeline') -> None:
            self._p = p

            self._single_handlers_by_type_cache: ta.Dict[type, ta.Optional[ta.Any]] = {}
            self._handlers_by_type_cache: ta.Dict[type, ta.Sequence[ta.Any]] = {}

        _handlers: ta.List[ChannelPipelineHandler]

        def handlers(self) -> ta.Sequence[ChannelPipelineHandler]:
            try:
                return self._handlers
            except AttributeError:
                pass

            lst: ta.List[ChannelPipelineHandler] = []
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                lst.append(ctx._handler)  # noqa

            self._handlers = lst
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

            ret: ta.List[ta.Any] = []
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                if isinstance(h := ctx._handler, ty):  # noqa
                    ret.append(h)

            self._handlers_by_type_cache[ty] = ret
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
            handlers: ta.Sequence[ChannelPipelineHandler] = (),
            *,
            scheduler: ta.Optional[ChannelPipelineScheduler] = None,
    ) -> None:
        super().__init__()

        self._scheduler: ta.Final[ta.Optional[ChannelPipelineScheduler]] = scheduler

        self._emitted_q: ta.Final[collections.deque[ta.Any]] = collections.deque()

        self._saw_close = False
        self._saw_eof = False

        self._pipeline: ta.Final[ChannelPipeline] = ChannelPipeline(self, handlers)  # final

        self._pending_inbound_must_propagate: ta.Final[ta.Dict[int, ta.Any]] = {}
        self._pending_outbound_must_propagate: ta.Final[ta.Dict[int, ta.Any]] = {}

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}()'

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

    def _removing(self, handler: ChannelPipelineHandler) -> None:
        if (sched := self._scheduler) is not None:
            sched.cancel_all(handler)

    #

    def _feed_in(self, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            self._saw_eof = True
        elif self._saw_eof:
            raise SawEofChannelPipelineError

        ctx = self._pipeline._outermost  # noqa
        try:
            ctx._inbound(msg)  # noqa
        except BaseException as e:  # noqa
            self.handle_error(e)

    def feed_in(self, msg: ta.Any) -> None:
        self._feed_in(msg)

    def feed_eof(self) -> None:
        self._feed_in(ChannelPipelineMessages.Eof())

    #

    def _feed_out(self, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Close):
            self._saw_close = True
        elif self._saw_close:
            raise ClosedChannelPipelineError

        ctx = self._pipeline._innermost  # noqa
        try:
            ctx._outbound(msg)  # noqa
        except BaseException as e:  # noqa
            self.handle_error(e)

    def feed_out(self, msg: ta.Any) -> None:
        self._feed_out(msg)

    def feed_close(self) -> None:
        self._feed_out(ChannelPipelineMessages.Close())

    #

    def emit(self, msg: ta.Any) -> None:
        self._emitted_q.append(msg)

    def poll(self) -> ta.Optional[ta.Any]:
        if not self._emitted_q:
            return None

        return self._emitted_q.popleft()

    def drain(self) -> ta.List[ta.Any]:
        out: ta.List[ta.Any] = []

        while self._emitted_q:
            out.append(self._emitted_q.popleft())

        return out

    #

    def handle_error(self, e: BaseException) -> None:
        self.emit(ChannelPipelineEvents.Error(e))

        if not self._saw_close:
            self.feed_close()

    #

    def _get_must_propagate_dct(self, d: ta.Literal['inbound', 'outbound']) -> ta.Dict[int, ta.Any]:
        if d == 'inbound':
            return self._pending_inbound_must_propagate
        elif d == 'outbound':
            return self._pending_outbound_must_propagate
        else:
            raise ValueError(d)

    def _add_must_propagate(
            self,
            d: ta.Literal['inbound', 'outbound'],
            msg: ChannelPipelineMessages.MustPropagate,
    ) -> None:
        dct = self._get_must_propagate_dct(d)

        i = id(msg)
        try:
            x = dct[i]
        except KeyError:
            pass
        else:
            check.is_(msg, x)
            return
        dct[i] = msg

    def _remove_must_propagate(
            self,
            d: ta.Literal['inbound', 'outbound'],
            msg: ChannelPipelineMessages.MustPropagate,
    ) -> None:
        dct = self._get_must_propagate_dct(d)

        i = id(msg)
        try:
            x = dct.pop(i)
        except KeyError:
            raise MessageNotPropagatedChannelPipelineError([msg]) from None
        if x is not msg:
            raise MessageNotPropagatedChannelPipelineError([msg])

    def check_propagated(self) -> None:
        lst: ta.List[ta.Any] = [
            *self._pending_inbound_must_propagate.values(),
            *self._pending_outbound_must_propagate.values(),
        ]
        if lst:
            raise MessageNotPropagatedChannelPipelineError(lst)
