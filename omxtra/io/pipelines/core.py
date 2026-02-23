# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import collections
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.namespaces import NamespaceClass

from .errors import ContextInvalidatedChannelPipelineError
from .errors import FinalOutputChannelPipelineError
from .errors import MessageNotPropagatedChannelPipelineError
from .errors import MessageReachedTerminalChannelPipelineError
from .errors import SawFinalInputChannelPipelineError
from .errors import UnhandleableChannelPipelineError


F = ta.TypeVar('F')
T = ta.TypeVar('T')

ChannelPipelineHandlerFn = ta.Callable[['ChannelPipelineHandlerContext', F], T]  # ta.TypeAlias

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
    class FinalInput(NeverOutbound, MustPropagate):  # ~ Netty `ChannelInboundHandler::channelInactive`
        """Signals that the inbound stream has produced its final message (`eof`)."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}@{id(self):x}()'

    @ta.final
    @dc.dataclass(frozen=True)
    class FinalOutput(NeverInbound, MustPropagate):  # ~ Netty `ChannelOutboundHandler::close`
        """Signals that the outbound stream has produced its final message (`close`)."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}@{id(self):x}()'

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class Error(NeverOutbound):
        """Signals an exception occurred in the pipeline."""

        exc: BaseException

        direction: ta.Optional['ChannelPipelineDirection'] = None
        handler: ta.Optional['ChannelPipelineHandlerRef'] = None


##


class ChannelPipelineHandlerNotification(Abstract):  # ~ Netty `ChannelHandler` methods
    """
    Directionless, private events sent to a specific handler that are not to be forwarded to any other handler in either
    direction.
    """


class ChannelPipelineHandlerNotifications(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class Added(ChannelPipelineHandlerNotification):
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class Removed(ChannelPipelineHandlerNotification):
        pass


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
    The embodiment of an instance of a handler at a position in a pipeline. Passed to ChannelPipelineHandler methods,
    providing handler-specific access to the pipeline and channel. As instances of `ShareableChannelPipelineHandler` may
    validly be simultaneously present at multiple positions in a pipeline, a single handler may have multiple active
    context instances associated with it in any given pipeline.

    Instances of this class are considered private to a handler instance and are not to be cached or shared in any way.
    The method names reflect this: they are operations available to the handler in the context of a pipeline processing
    operation.
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
    def handler(self) -> 'ChannelPipelineHandler':
        return self._handler

    @property
    def name(self) -> ta.Optional[str]:
        return self._name

    #

    def defer(self, fn: ta.Callable[['ChannelPipelineHandlerContext'], None], *, first: bool = False) -> None:
        self._pipeline._channel._defer(self, fn, first=first)  # noqa

    def defer_no_context(self, fn: ta.Callable[[], None], *, first: bool = False) -> None:
        self._pipeline._channel._defer(self, fn, no_context=True, first=first)  # noqa

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

    ##
    # Feeding `type`'s is forbidden as it's almost always going to be an error - usually forgetting to instantiate a
    # marker dataclass)

    _FORBIDDEN_INBOUND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        ChannelPipelineMessages.NeverInbound,
        ChannelPipelineHandlerNotification,
        type,
    )

    def _inbound(self, msg: ta.Any) -> None:
        if self._invalidated:
            raise ContextInvalidatedChannelPipelineError
        check.not_isinstance(msg, self._FORBIDDEN_INBOUND_TYPES)
        check.state(self._pipeline._channel._execution_depth > 0)  # noqa

        if isinstance(msg, ChannelPipelineMessages.MustPropagate):
            self._pipeline._channel._propagation.add_must(self, 'inbound', msg)  # noqa

        try:
            self._handler.inbound(self, msg)
        except UnhandleableChannelPipelineError:
            raise
        except BaseException as e:
            if self._handling_error or self._pipeline._config.raise_immediately:  # noqa
                raise
            self._handle_error(e, 'inbound')

    _FORBIDDEN_OUTBOUND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        ChannelPipelineMessages.NeverOutbound,
        ChannelPipelineHandlerNotification,
        type,
    )

    def _outbound(self, msg: ta.Any) -> None:
        if self._invalidated:
            raise ContextInvalidatedChannelPipelineError
        check.not_isinstance(msg, self._FORBIDDEN_OUTBOUND_TYPES)
        check.state(self._pipeline._channel._execution_depth > 0)  # noqa

        if isinstance(msg, ChannelPipelineMessages.MustPropagate):
            self._pipeline._channel._propagation.add_must(self, 'outbound', msg)  # noqa

        try:
            self._handler.outbound(self, msg)
        except UnhandleableChannelPipelineError:
            raise
        except BaseException as e:
            if self._handling_error or self._pipeline._config.raise_immediately:  # noqa
                raise
            self._handle_error(e, 'outbound')

    #

    _handling_error: bool = False

    def _handle_error(self, e: BaseException, direction: 'ChannelPipelineDirection') -> None:
        check.state(not self._handling_error)
        self._handling_error = True

        try:
            try:
                self.feed_in(ChannelPipelineMessages.Error(e, direction, self._ref))
            except UnhandleableChannelPipelineError:  # noqa
                raise
            except BaseException as e2:  # noqa
                raise

        finally:
            self._handling_error = False

    ##
    # The following overloads attempts to catch invalid inputs statically, but there's no explicit way to do this in
    # mypy - the following trick only works if there's an unconditional statement after the attempted calls, but it's
    # better than nothing.

    @ta.overload
    def feed_in(
            self,
            msg: ta.Union[
                ChannelPipelineMessages.NeverInbound,
                ChannelPipelineHandlerNotification,
                type,
            ],
    ) -> 'ta.Never':
        ...

    @ta.overload
    def feed_in(self, msg: object) -> None:
        ...

    def feed_in(self, msg):  # ~ Netty `ChannelInboundInvoker::fireChannelRead`
        nxt = self._next_in
        while not nxt._handles_inbound:  # noqa
            nxt = nxt._next_in  # noqa
        nxt._inbound(msg)  # noqa

    @ta.overload
    def feed_out(
            self,
            msg: ta.Union[
                ChannelPipelineMessages.NeverOutbound,
                ChannelPipelineHandlerNotification,
                type,
            ],
    ) -> 'ta.Never':
        ...

    @ta.overload
    def feed_out(self, msg: object) -> None:
        ...

    def feed_out(self, msg):  # ~ Netty `ChannelOutboundInvoker::write`
        nxt = self._next_out  # noqa
        while not nxt._handles_outbound:  # noqa
            nxt = nxt._next_out  # noqa
        nxt._outbound(msg)  # noqa

    #

    def feed_final_output(self) -> None:
        self.feed_out(ChannelPipelineMessages.FinalOutput())

##


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

    def notify(self, ctx: ChannelPipelineHandlerContext, no: ChannelPipelineHandlerNotification) -> None:
        pass

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_in(msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_out(msg)


class ShareableChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    pass


##


ChannelPipelineDirection = ta.Literal['inbound', 'outbound']  # ta.TypeAlias  # omlish-amalg-typing-no-move

ChannelPipelineDirectionOrDuplex = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    ChannelPipelineDirection,
    'duplex',
]

ChannelPipelineHandlerUpdate = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'adding',
    'added',
    'removing',
    'removed',
]


@ta.final
class ChannelPipeline:
    @ta.final
    @dc.dataclass(frozen=True)
    class Config:
        raise_immediately: bool = False

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

        self._channel._handler_update(ctx, 'adding')  # noqa

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

        self._channel._handler_update(ctx, 'added')  # noqa

        # FIXME: exceptions?
        handler.notify(ctx, ChannelPipelineHandlerNotifications.Added())

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

        self._channel._handler_update(ctx, 'removing')  # noqa

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

        self._channel._handler_update(ctx, 'removed')  # noqa

        # FIXME: exceptions? defer?
        handler.notify(ctx, ChannelPipelineHandlerNotifications.Removed())

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
        """'Head' in Netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def outbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._propagation.remove_must(ctx, 'outbound', msg)  # noqa

            ctx._pipeline._channel._terminal_outbound(ctx, msg)  # noqa

    class _Innermost(ChannelPipelineHandler):
        """'Tail' in Netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._propagation.remove_must(ctx, 'inbound', msg)  # noqa

            ctx._pipeline._channel._terminal_inbound(ctx, msg)  # noqa

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

    @dc.dataclass(frozen=True)
    class HandlerType(ta.Generic[T]):
        """This is entirely just a workaround for mypy's `type-abstract` deficiency."""

        ty: ta.Type[T]

    def find_handlers_of_type(
            self,
            ty: ta.Union[HandlerType[T], ta.Type[T]],
    ) -> ta.Sequence[ChannelPipelineHandlerRef[T]]:
        if isinstance(ty, ChannelPipeline.HandlerType):
            ty = ty.ty
        return self._caches().find_handlers_of_type(ty)

    def find_single_handler_of_type(
            self,
            ty: ta.Union[HandlerType[T], ta.Type[T]],
    ) -> ta.Optional[ChannelPipelineHandlerRef[T]]:
        if isinstance(ty, ChannelPipeline.HandlerType):
            ty = ty.ty
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


class ChannelPipelineService(Abstract):
    def handler_update(self, handler_ref: ChannelPipelineHandlerRef, kind: ChannelPipelineHandlerUpdate) -> None:
        pass


##


@ta.final
class PipelineChannel:
    @ta.final
    @dc.dataclass(frozen=True)
    class Config:
        # TODO: 'close'? 'deadletter'? combination? composition? ...
        inbound_terminal: ta.Literal['drop', 'raise'] = 'raise'

        disable_propagation_checking: bool = False

        pipeline: ChannelPipeline.Config = ChannelPipeline.Config()

        def __post_init__(self) -> None:
            check.in_(self.inbound_terminal, ('drop', 'raise'))

    # Available here for user convenience (so configuration of a PipelineChannel's ChannelPipeline doesn't require
    # actually importing ChannelPipeline to get to its Config class).
    PipelineConfig: ta.ClassVar[ta.Type[ChannelPipeline.Config]] = ChannelPipeline.Config

    def __init__(
            self,
            handlers: ta.Sequence[ChannelPipelineHandler] = (),
            config: Config = Config(),
            *,
            services: ta.Optional[ta.Sequence[ChannelPipelineService]] = None,
    ) -> None:
        super().__init__()

        self._config: ta.Final[PipelineChannel.Config] = config

        self._services: ta.Final[PipelineChannel._Services] = PipelineChannel._Services(services or [])

        self._out_q: ta.Final[collections.deque[ta.Any]] = collections.deque()

        self._saw_final_input = False
        self._saw_final_output = False

        self._pipeline: ta.Final[ChannelPipeline] = ChannelPipeline(
            self,
            handlers,
            config=config.pipeline,
        )

        self._execution_depth = 0

        self._deferred: collections.deque[PipelineChannel._Deferred] = collections.deque()

        self._propagation: PipelineChannel._Propagation = PipelineChannel._Propagation(self)

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    @property
    def pipeline(self) -> ChannelPipeline:
        return self._pipeline

    #

    @property
    def saw_final_input(self) -> bool:
        return self._saw_final_input  # Note: only 'channel-level'

    @property
    def saw_final_output(self) -> bool:
        return self._saw_final_output

    #

    class _Services:
        def __init__(self, lst: ta.Sequence[ChannelPipelineService]) -> None:
            self._lst = lst

            self._by_type_cache: ta.Dict[type, ta.Sequence[ta.Any]] = {}
            self._single_by_type_cache: ta.Dict[type, ta.Optional[ta.Any]] = {}

        def __len__(self) -> int:
            return len(self._lst)

        def __iter__(self) -> ta.Iterator[ChannelPipelineService]:
            return iter(self._lst)

        def __contains__(self, item: ta.Any) -> bool:
            return item in self._lst

        @dc.dataclass(frozen=True)
        class ServiceType(ta.Generic[T]):
            """This is entirely just a workaround for mypy's `type-abstract` deficiency."""

            ty: ta.Type[T]

        def find_all(self, ty: ta.Union[ServiceType[T], ta.Type[T]]) -> ta.Sequence[T]:
            if isinstance(ty, self.ServiceType):
                ty = ty.ty

            try:
                return self._by_type_cache[ty]
            except KeyError:
                pass

            self._by_type_cache[ty] = ret = [svc for svc in self._lst if isinstance(svc, ty)]
            return ret

        def find(self, ty: ta.Union[ServiceType[T], ta.Type[T]]) -> ta.Optional[T]:
            if isinstance(ty, self.ServiceType):
                ty = ty.ty

            try:
                return self._single_by_type_cache[ty]
            except KeyError:
                pass

            self._single_by_type_cache[ty] = ret = check.opt_single(self.find_all(ty))
            return ret

        def __getitem__(self, ty: ta.Union[ServiceType[T], ta.Type[T]]) -> T:
            if (svc := self.find(ty)) is None:
                raise KeyError(ty)
            return svc

    @property
    def services(self) -> _Services:
        return self._services

    #

    def _handler_update(self, ctx: ChannelPipelineHandlerContext, kind: ChannelPipelineHandlerUpdate) -> None:
        for svc in self._services._lst:  # noqa
            svc.handler_update(ctx._ref, kind)  # noqa

    #

    class _Deferred(ta.NamedTuple):
        ctx: ChannelPipelineHandlerContext

        fn: ta.Union[
            ta.Callable[[ChannelPipelineHandlerContext], None],
            ta.Callable[[], None],
        ]

        no_context: bool

    def _defer(
            self,
            ctx: ChannelPipelineHandlerContext,
            fn: ta.Union[
                ta.Callable[[ChannelPipelineHandlerContext], None],
                ta.Callable[[], None],
            ],
            *,
            no_context: bool = False,
            first: bool = False,
    ) -> None:
        dfl = PipelineChannel._Deferred(ctx, fn, no_context)
        if first:
            self._deferred.appendleft(dfl)
        else:
            self._deferred.append(dfl)

    def _maybe_execute_deferred(self) -> None:
        # TODO: errors lol
        # TODO: meditate on reentrancy lol
        while self._deferred and not self._execution_depth:
            dfl = self._deferred.popleft()

            if dfl.no_context:
                dfl.fn()  # type: ignore[call-arg]
            else:
                dfl.fn(dfl.ctx)  # type: ignore[call-arg]

    #

    def _step_in(self) -> None:
        self._execution_depth += 1

    def _step_out(self) -> None:
        check.state(self._execution_depth > 0)
        self._execution_depth -= 1

        self._maybe_execute_deferred()

        if not self._execution_depth:
            self._propagation.check_and_clear()

    #

    def _feed_in_to(self, ctx: ChannelPipelineHandlerContext, msgs: ta.Iterable[ta.Any]) -> None:
        self._step_in()
        try:
            for msg in msgs:
                if isinstance(msg, ChannelPipelineMessages.FinalInput):
                    self._saw_final_input = True
                elif self._saw_final_input:
                    raise SawFinalInputChannelPipelineError  # noqa

                ctx._inbound(msg)  # noqa

        finally:
            self._step_out()

    def feed_in_to(self, handler_ref: ChannelPipelineHandlerRef, *msgs: ta.Any) -> None:
        # TODO: remove? internal only? used by replace-self pattern
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self._pipeline)  # noqa
        self._feed_in_to(ctx, msgs)

    def feed_in(self, *msgs: ta.Any) -> None:
        self._feed_in_to(self._pipeline._outermost, msgs)  # noqa

    def feed_final_input(self) -> None:
        self._feed_in_to(self._pipeline._outermost, (ChannelPipelineMessages.FinalInput(),))  # noqa

    #

    def _terminal_inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:  # noqa
        if (tm := self._config.inbound_terminal) == 'drop':
            pass

        elif tm == 'raise':
            if not isinstance(msg, ChannelPipelineMessages.MustPropagate):
                raise MessageReachedTerminalChannelPipelineError(inbound=msg)

        else:
            raise RuntimeError(f'unknown inbound terminal mode {tm}')

    def _terminal_outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:  # noqa
        if isinstance(msg, ChannelPipelineMessages.FinalOutput):
            self._saw_final_output = True
        elif self._saw_final_output:
            raise FinalOutputChannelPipelineError

        self._out_q.append(msg)

    #

    def poll(self) -> ta.Optional[ta.Any]:
        if not self._out_q:
            return None

        return self._out_q.popleft()

    def drain(self) -> ta.List[ta.Any]:
        out: ta.List[ta.Any] = []

        while self._out_q:
            out.append(self._out_q.popleft())

        return out

    #

    @ta.final
    class _Propagation:
        def __init__(self, ch: 'PipelineChannel') -> None:
            self._ch = ch

            self._pending_inbound_must: ta.Final[ta.Dict[int, ta.Tuple[ta.Any, ChannelPipelineHandlerContext]]] = {}
            self._pending_outbound_must: ta.Final[ta.Dict[int, ta.Tuple[ta.Any, ChannelPipelineHandlerContext]]] = {}

        def _get_must_dict(self, direction: ChannelPipelineDirection) -> ta.Dict[int, ta.Any]:
            if direction == 'inbound':
                return self._pending_inbound_must
            elif direction == 'outbound':
                return self._pending_outbound_must
            else:
                raise RuntimeError(f'Unknown direction {direction}')

        def add_must(
                self,
                ctx: ChannelPipelineHandlerContext,
                direction: ChannelPipelineDirection,
                msg: ChannelPipelineMessages.MustPropagate,
        ) -> None:
            if self._ch._config.disable_propagation_checking:  # noqa
                return

            dct = self._get_must_dict(direction)

            i = id(msg)
            try:
                x, last_ctx = dct[i]  # noqa
            except KeyError:
                pass
            else:
                check.is_(msg, x)
            dct[i] = (msg, ctx)

        def remove_must(
                self,
                ctx: ChannelPipelineHandlerContext,
                direction: ChannelPipelineDirection,
                msg: ChannelPipelineMessages.MustPropagate,
        ) -> None:
            if self._ch._config.disable_propagation_checking:  # noqa
                return

            dct = self._get_must_dict(direction)

            i = id(msg)
            try:
                x, last_ctx = dct.pop(i)  # noqa
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

        def check_and_clear(self) -> None:
            if self._ch._config.disable_propagation_checking:  # noqa
                return

            if not (self._pending_inbound_must or self._pending_outbound_must):
                return

            inbound = [msg for msg, _ in self._pending_inbound_must.values()]
            outbound = [msg for msg, _ in self._pending_outbound_must.values()]

            self._pending_inbound_must.clear()
            self._pending_outbound_must.clear()

            raise MessageNotPropagatedChannelPipelineError(
                inbound=inbound or None,
                outbound=outbound or None,
            )
