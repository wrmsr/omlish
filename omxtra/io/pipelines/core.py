# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
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
from .errors import MessageReachedTerminalChannelPipelineError
from .errors import SawEofChannelPipelineError


T = ta.TypeVar('T')

ChannelPipelineHandlerT = ta.TypeVar('ChannelPipelineHandlerT', bound='ChannelPipelineHandler')
ShareableChannelPipelineHandlerT = ta.TypeVar('ShareableChannelPipelineHandlerT', bound='ShareableChannelPipelineHandler')  # noqa


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


##


@ta.final
class ChannelPipelineHandlerRef(ta.Generic[T]):
    """
    Encapsulates a reference to a unique position of a handler instance in a pipeline, used at public api boundaries.

    Should the handler be removed from the relevant position in the pipeline, the ref instance becomes permanently
    invalidated.

    Note that this is definitionally identity hash/eq: given some valid ref, removing that ref from the pipeline and
    re-adding the same handler instance to the same effective position in a pipeline results in a different ref.
    """

    def __init__(self, *, _context: 'ChannelPipelineHandlerContext') -> None:
        self._context = _context

    @property
    def pipeline(self) -> 'ChannelPipeline':
        return self._context._pipeline  # noqa

    @property
    def channel(self) -> 'PipelineChannel':
        return self._context._pipeline._channel  # noqa

    @property
    def handler(self) -> T:
        return self._context._handler  # type: ignore[return-value]  # noqa

    @property
    def name(self) -> ta.Optional[str]:
        return self._context._name  # noqa

    @property
    def invalidated(self) -> bool:
        return self._context._invalidated  # noqa

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}'
            f'{"!INVALIDATED" if self.invalidated else ""}'
            f'{f"<{self.name!r}>" if self.name is not None else ""}'
            f'<context@{id(self._context):x}>'
            f'({self.handler!r}@{id(self.handler):x})'
        )


ChannelPipelineHandlerRef_ = ChannelPipelineHandlerRef['ChannelPipelineHandler']  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


@ta.final
class ChannelPipelineHandlerContext:
    """
    Passed to ChannelPipelineHandler methods, provides handler-specific access and operations to the pipeline channel.
    As instances of `ShareableChannelPipelineHandler` may validly be present in multiple

    Instances of this class are considered private to a handler instance and are not to be cached or shared in any way.
    """

    def __init__(
            self,
            *,
            _pipeline: 'ChannelPipeline',
            _handler: 'ChannelPipelineHandler',

            name: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._pipeline: ta.Final[ChannelPipeline] = _pipeline
        self._handler: ta.Final[ChannelPipelineHandler] = _handler

        self._name: ta.Final[ta.Optional[str]] = name

        self._ref: ChannelPipelineHandlerRef_ = ChannelPipelineHandlerRef(_context=self)

        self._handles_inbound = type(_handler).inbound is not ChannelPipelineHandler.inbound
        self._handles_outbound = type(_handler).outbound is not ChannelPipelineHandler.outbound

    _next_in: 'ChannelPipelineHandlerContext'  # 'next'
    _next_out: 'ChannelPipelineHandlerContext'  # 'prev'

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}@{id(self):x}'
            f'{"!INVALIDATED" if self._invalidated else ""}'
            f'{f"<{self._name!r}>" if self._name is not None else ""}'
            f'<pipeline@{id(self.pipeline):x}>'
            f'({self._handler!r}@{id(self._handler):x})'
        )

    @property
    def ref(self) -> ChannelPipelineHandlerRef_:
        return self._ref

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

    @property
    def name(self) -> ta.Optional[str]:
        return self._name

    #

    _invalidated = False

    @property
    def invalidated(self) -> bool:
        return self._invalidated

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class StorageKey(ta.Generic[T]):
        name: str

    @ta.final
    class Storage:
        def __init__(self) -> None:
            self.__dict: ta.Dict[ChannelPipelineHandlerContext.StorageKey, ta.Any] = {}

        @property
        def dict(self) -> ta.Dict['ChannelPipelineHandlerContext.StorageKey', ta.Any]:
            return self.__dict

        def __getitem__(self, key: 'ChannelPipelineHandlerContext.StorageKey[T]') -> T:
            return self.__dict[key]

        @ta.overload
        def get(
                self,
                key: 'ChannelPipelineHandlerContext.StorageKey[T]',
                default: T,
                /,
        ) -> T:
            ...

        @ta.overload
        def get(
                self,
                key: 'ChannelPipelineHandlerContext.StorageKey[T]',
                default: ta.Optional[T] = None,
                /,
        ) -> ta.Optional[T]:
            ...

        def get(self, key, default=None, /):
            return self.__dict.get(key, default)

        def __setitem__(self, key: 'ChannelPipelineHandlerContext.StorageKey[T]', value: T) -> None:
            self.__dict[key] = value

        def __delitem__(self, key: 'ChannelPipelineHandlerContext.StorageKey[T]') -> None:
            del self.__dict[key]

        def __len__(self) -> int:
            return len(self.__dict)

        def __contains__(self, key: 'ChannelPipelineHandlerContext.StorageKey[T]') -> bool:
            return key in self.__dict

        def __iter__(self) -> ta.Iterator['ChannelPipelineHandlerContext.StorageKey[T]']:
            return iter(self.__dict)

        def items(self) -> ta.Iterator[ta.Tuple['ChannelPipelineHandlerContext.StorageKey[T]', T]]:
            return iter(self.__dict.items())

    _storage_: Storage

    @property
    def storage(self) -> Storage:
        try:
            return self._storage_
        except AttributeError:
            pass
        self._storage_ = ret = ChannelPipelineHandlerContext.Storage()
        return ret

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


class ChannelPipelineHandler(Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if not (
            cls.__hash__ is object.__hash__ and
            cls.__eq__ is object.__eq__ and
            cls.__ne__ is object.__ne__
        ):
            raise TypeError(
                f'ChannelPipelineHandler subclass {cls.__name__} must not override __hash__, __eq__ or __ne__',
            )

    #

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


class ShareableChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    pass


##


ChannelPipelineDirection = ta.Literal['inbound', 'outbound']  # ta.TypeAlias  # omlish-amalg-typing-no-move
ChannelPipelineDirectionOrDuplex = ta.Literal[ChannelPipelineDirection, 'duplex']  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


@ta.final
class ChannelPipeline:
    @ta.final
    @dc.dataclass(frozen=True)
    class Config:
        terminal_mode: ta.Literal['drop', 'emit', 'raise'] = 'raise'

        def __post_init__(self) -> None:
            check.in_(self.terminal_mode, ('drop', 'emit', 'raise'))

    def __init__(
            self,
            channel: 'PipelineChannel',
            handlers: ta.Sequence[ChannelPipelineHandler] = (),
            config: Config = Config(),
    ) -> None:
        super().__init__()

        self._channel: ta.Final[PipelineChannel] = channel
        self._config: ta.Final[ChannelPipeline.Config] = config

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

        self._unique_contexts: ta.Final[ta.Dict[ChannelPipelineHandler, ChannelPipelineHandlerContext]] = {}
        self._shareable_contexts: ta.Final[ta.Dict[ShareableChannelPipelineHandler, ta.Set[ChannelPipelineHandlerContext]]] = {}  # noqa

        self._contexts_by_name: ta.Final[ta.Dict[str, ChannelPipelineHandlerContext]] = {}

        for h in handlers:
            self.add_innermost(h)

    _outermost: ta.Final[ChannelPipelineHandlerContext]
    _innermost: ta.Final[ChannelPipelineHandlerContext]

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    #

    def feed_in_to(self, handler_ref: ChannelPipelineHandlerRef, msg: ta.Any) -> None:
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self)  # noqa
        ctx._inbound(msg)  # noqa

    def feed_out_to(self, handler_ref: ChannelPipelineHandlerRef, msg: ta.Any) -> None:
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self)  # noqa
        ctx._outbound(msg)  # noqa

    #

    def _check_can_add(
            self,
            handler: ChannelPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> ChannelPipelineHandler:
        if not isinstance(handler, ShareableChannelPipelineHandler):
            check.not_in(handler, self._unique_contexts)

        if name is not None:
            check.not_in(name, self._contexts_by_name)

        return handler

    def _check_can_add_relative_to(self, ctx: ChannelPipelineHandlerContext) -> ChannelPipelineHandlerContext:
        check.is_(ctx._pipeline, self)  # noqa
        check.state(not ctx._invalidated)  # noqa

        return ctx

    def _add(
            self,
            handler: ChannelPipelineHandler,
            *,
            inner_to: ta.Optional[ChannelPipelineHandlerContext] = None,
            outer_to: ta.Optional[ChannelPipelineHandlerContext] = None,

            name: ta.Optional[str] = None,
    ) -> ChannelPipelineHandlerRef:
        self._check_can_add(handler, name=name)

        if inner_to is not None:
            check.none(outer_to)
            check.is_not(inner_to, self._innermost)
            self._check_can_add_relative_to(inner_to)
        elif outer_to is not None:
            check.none(inner_to)
            check.is_not(outer_to, self._outermost)
            self._check_can_add_relative_to(outer_to)
        else:
            raise ValueError('Must specify exactly one of inner_to or outer_to')

        ctx = ChannelPipelineHandlerContext(
            _pipeline=self,
            _handler=handler,

            name=name,
        )

        if isinstance(handler, ShareableChannelPipelineHandler):
            self._shareable_contexts.setdefault(handler, set()).add(ctx)
        else:
            check.not_in(handler, self._unique_contexts)  # also pre-checked by _check_can_add
            self._unique_contexts[handler] = ctx

        if name is not None:
            self._contexts_by_name[name] = ctx

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

        # FIXME: exceptions?
        handler.added(ctx)

        return ctx._ref  # noqa

    def add_innermost(
            self,
            handler: ChannelPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> ChannelPipelineHandlerRef:
        return self._add(handler, outer_to=self._innermost, name=name)

    def add_outermost(
            self,
            handler: ChannelPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> ChannelPipelineHandlerRef:
        return self._add(handler, inner_to=self._outermost, name=name)

    def add_inner_to(
            self,
            inner_to: ChannelPipelineHandlerRef,
            handler: ChannelPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> ChannelPipelineHandlerRef:
        ctx = inner_to._context   # noqa
        return self._add(handler, inner_to=ctx, name=name)

    def add_outer_to(
            self,
            outer_to: ChannelPipelineHandlerRef,
            handler: ChannelPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> ChannelPipelineHandlerRef:
        ctx = outer_to._context   # noqa
        return self._add(handler, outer_to=ctx, name=name)

    #

    def _check_can_remove(self, handler_ref: ChannelPipelineHandlerRef) -> ChannelPipelineHandler:
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self)  # noqa

        check.state(not ctx._invalidated)  # noqa

        handler = ctx._handler  # noqa
        if isinstance(handler, ShareableChannelPipelineHandler):
            check.in_(ctx, self._shareable_contexts[handler])
        else:
            check.equal(ctx, self._unique_contexts[handler])

        check.is_not(ctx, self._innermost)
        check.is_not(ctx, self._outermost)

        return handler

    def _remove(self, handler_ref: ChannelPipelineHandlerRef) -> None:
        self._check_can_remove(handler_ref)

        ctx = handler_ref._context  # noqa
        handler = ctx._handler  # noqa

        self._channel._removing(ctx._ref)  # noqa

        # FIXME: exceptions? defer?
        handler.removing(ctx)

        if ctx._name is not None:  # noqa
            del self._contexts_by_name[ctx._name]  # noqa

        if isinstance(handler, ShareableChannelPipelineHandler):
            cs = self._shareable_contexts[handler]
            cs.remove(ctx)
            if not cs:
                del self._shareable_contexts[handler]
        else:
            del self._unique_contexts[handler]

        ctx._next_in._next_out = ctx._next_out  # noqa
        ctx._next_out._next_in = ctx._next_in  # noqa

        ctx._invalidated = True  # noqa
        del ctx._next_in  # noqa
        del ctx._next_out  # noqa

        self._clear_caches()

    def remove(self, handler_ref: ChannelPipelineHandlerRef) -> None:
        self._remove(handler_ref)

    #

    def replace(
            self,
            old_handler_ref: ChannelPipelineHandlerRef,
            new_handler: ChannelPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> ChannelPipelineHandlerRef:
        self._check_can_remove(old_handler_ref)
        self._check_can_add(new_handler, name=name)

        inner_to = old_handler_ref._context._next_out  # noqa
        self._remove(old_handler_ref)
        return self._add(new_handler, inner_to=inner_to, name=name)

    #

    class _Outermost(ChannelPipelineHandler):
        """'Head' in netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def outbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._remove_must_propagate('outbound', msg)  # noqa

            ctx._pipeline._terminal('outbound', ctx, msg)  # noqa

    class _Innermost(ChannelPipelineHandler):
        """'Tail' in netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._remove_must_propagate('inbound', msg)  # noqa

            ctx._pipeline._terminal('inbound', ctx, msg)  # noqa

    def _terminal(self, direction: ChannelPipelineDirection, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if (tm := self._config.terminal_mode) == 'drop':
            pass

        elif tm == 'emit':
            ctx.emit(msg)

        elif tm == 'raise':
            if not isinstance(msg, ChannelPipelineMessages.MustPropagate):
                raise MessageReachedTerminalChannelPipelineError(
                    inbound=[msg] if direction == 'inbound' else None,
                    outbound=[msg] if direction == 'outbound' else None,
                )

        else:
            raise RuntimeError(f'unknown terminal mode {tm}')

    #

    class _Caches:
        def __init__(self, p: 'ChannelPipeline') -> None:
            self._p = p

            self._handlers_by_type_cache: ta.Dict[type, ta.Sequence[ChannelPipelineHandlerRef]] = {}
            self._single_handlers_by_type_cache: ta.Dict[type, ta.Optional[ChannelPipelineHandlerRef]] = {}

        _handlers: ta.Sequence[ChannelPipelineHandlerRef_]

        def handlers(self) -> ta.Sequence[ChannelPipelineHandlerRef_]:
            try:
                return self._handlers
            except AttributeError:
                pass

            lst: ta.List[ChannelPipelineHandlerRef_] = []
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                lst.append(ctx._ref)  # noqa

            self._handlers = lst
            return lst

        _handlers_by_name: ta.Mapping[str, ChannelPipelineHandlerRef_]

        def handlers_by_name(self) -> ta.Mapping[str, ChannelPipelineHandlerRef_]:
            try:
                return self._handlers_by_name
            except AttributeError:
                pass

            dct: ta.Dict[str, ChannelPipelineHandlerRef_] = {}
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                if (n := ctx._name) is not None:  # noqa
                    dct[n] = ctx._ref  # noqa

            self._handlers_by_name = dct
            return dct

        def find_handlers_of_type(self, ty: ta.Type[T]) -> ta.Sequence[ChannelPipelineHandlerRef[T]]:
            try:
                return self._handlers_by_type_cache[ty]
            except KeyError:
                pass

            ret: ta.List[ta.Any] = []
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                if isinstance(ctx._handler, ty):  # noqa
                    ret.append(ctx._ref)  # noqa

            self._handlers_by_type_cache[ty] = ret
            return ret

        def find_single_handler_of_type(self, ty: ta.Type[T]) -> ta.Optional[ChannelPipelineHandlerRef[T]]:
            try:
                return self._single_handlers_by_type_cache[ty]
            except KeyError:
                pass

            self._single_handlers_by_type_cache[ty] = ret = check.opt_single(self.find_handlers_of_type(ty))
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

    def handlers(self) -> ta.Sequence[ChannelPipelineHandlerRef]:
        return self._caches().handlers()

    def handlers_by_name(self) -> ta.Mapping[str, ChannelPipelineHandlerRef_]:
        return self._caches().handlers_by_name()

    def find_handlers_of_type(self, ty: ta.Type[T]) -> ta.Sequence[ChannelPipelineHandlerRef[T]]:
        return self._caches().find_handlers_of_type(ty)

    def find_single_handler_of_type(self, ty: ta.Type[T]) -> ta.Optional[ChannelPipelineHandlerRef[T]]:
        return self._caches().find_single_handler_of_type(ty)

    #

    @ta.overload
    def find_handler(  # type: ignore[overload-overlap]
            self,
            handler: ShareableChannelPipelineHandlerT,
    ) -> ta.Sequence[ChannelPipelineHandlerRef[ShareableChannelPipelineHandlerT]]:
        ...

    @ta.overload
    def find_handler(
            self,
            handler: ChannelPipelineHandlerT,
    ) -> ta.Optional[ChannelPipelineHandlerRef[ChannelPipelineHandlerT]]:
        ...

    def find_handler(self, handler):
        if isinstance(handler, ShareableChannelPipelineHandler):
            out: ta.List[ta.Any] = []
            ctx = self._outermost
            while (ctx := ctx._next_in) is not self._innermost:  # noqa
                if handler == ctx._handler:  # noqa
                    out.append(ctx._ref)  # noqa
            return out

        else:
            # Relies on existing uniqueness checks
            ctx = self._outermost
            while (ctx := ctx._next_in) is not self._innermost:  # noqa
                if handler == ctx._handler:  # noqa
                    return ctx._ref  # noqa
            return None


##


class ChannelPipelineScheduler(Abstract):
    class Handle(Abstract):
        @abc.abstractmethod
        def cancel(self) -> None:
            raise NotImplementedError

    @abc.abstractmethod
    def schedule(self, handler_ref: ChannelPipelineHandlerRef, msg: ta.Any) -> Handle:
        raise NotImplementedError

    @abc.abstractmethod
    def cancel_all(self, handler_ref: ta.Optional[ChannelPipelineHandlerRef] = None) -> None:
        raise NotImplementedError


##


@ta.final
class PipelineChannel:
    @ta.final
    @dc.dataclass(frozen=True)
    class Config:
        raise_handler_errors: bool = False

        pipeline: ChannelPipeline.Config = ChannelPipeline.Config()

    # Available here for user convenience (so configuration of a PipelineChannel's ChannelPipeline doesn't require
    # actually importing ChannelPipeline to get to its Config class).
    PipelineConfig: ta.ClassVar[ta.Type[ChannelPipeline.Config]] = ChannelPipeline.Config

    def __init__(
            self,
            handlers: ta.Sequence[ChannelPipelineHandler] = (),
            config: Config = Config(),
            *,
            scheduler: ta.Optional[ChannelPipelineScheduler] = None,
    ) -> None:
        super().__init__()

        self._config: ta.Final[PipelineChannel.Config] = config
        self._scheduler: ta.Final[ta.Optional[ChannelPipelineScheduler]] = scheduler

        self._emitted_q: ta.Final[collections.deque[ta.Any]] = collections.deque()

        self._saw_close = False
        self._saw_eof = False

        self._pipeline: ta.Final[ChannelPipeline] = ChannelPipeline(
            self,
            handlers,
            config=config.pipeline,
        )

        self._pending_inbound_must_propagate: ta.Final[ta.Dict[int, ta.Any]] = {}
        self._pending_outbound_must_propagate: ta.Final[ta.Dict[int, ta.Any]] = {}

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

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

    def _removing(self, handler_ref: ChannelPipelineHandlerRef) -> None:
        if (sched := self._scheduler) is not None:
            sched.cancel_all(handler_ref)

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
            if self._config.raise_handler_errors:
                raise
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
            if self._config.raise_handler_errors:
                raise
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

    def _get_must_propagate_dct(self, direction: ChannelPipelineDirection) -> ta.Dict[int, ta.Any]:
        if direction == 'inbound':
            return self._pending_inbound_must_propagate
        elif direction == 'outbound':
            return self._pending_outbound_must_propagate
        else:
            raise RuntimeError(f'Unknown direction {direction}')

    def _add_must_propagate(
            self,
            direction: ChannelPipelineDirection,
            msg: ChannelPipelineMessages.MustPropagate,
    ) -> None:
        dct = self._get_must_propagate_dct(direction)

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
            direction: ChannelPipelineDirection,
            msg: ChannelPipelineMessages.MustPropagate,
    ) -> None:
        dct = self._get_must_propagate_dct(direction)

        i = id(msg)
        try:
            x = dct.pop(i)
        except KeyError:
            raise MessageNotPropagatedChannelPipelineError(
                inbound=[msg] if direction == 'inbound' else None,
                outbound=[msg] if direction == 'outbound' else None,
            ) from None

        if x is not msg:
            raise MessageNotPropagatedChannelPipelineError(
                inbound=[msg] if direction == 'inbound' else None,
                outbound=[msg] if direction == 'outbound' else None,
            )

    def check_propagated(self) -> None:
        inbound = list(self._pending_inbound_must_propagate.values())
        outbound = list(self._pending_outbound_must_propagate.values())
        if inbound or outbound:
            raise MessageNotPropagatedChannelPipelineError(
                inbound=inbound or None,
                outbound=outbound or None,
            )
