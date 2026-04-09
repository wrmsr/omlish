# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import abc
import collections
import dataclasses as dc
import enum
import typing as ta

from ...lite.abstract import Abstract
from ...lite.check import check
from ...lite.namespaces import NamespaceClass
from .errors import ContextInvalidatedIoPipelineError
from .errors import MessageNotPropagatedIoPipelineError
from .errors import MessageReachedTerminalIoPipelineError
from .errors import SawFinalInputIoPipelineError
from .errors import SawFinalOutputIoPipelineError
from .errors import SawInitialInputIoPipelineError
from .errors import UnhandleableIoPipelineError


F = ta.TypeVar('F')
T = ta.TypeVar('T')

IoPipelineHandlerFn = ta.Callable[['IoPipelineHandlerContext', F], T]  # ta.TypeAlias

IoPipelineHandlerT = ta.TypeVar('IoPipelineHandlerT', bound='IoPipelineHandler')
ShareableIoPipelineHandlerT = ta.TypeVar('ShareableIoPipelineHandlerT', bound='ShareableIoPipelineHandler')  # noqa

IoPipelineMetadataT = ta.TypeVar('IoPipelineMetadataT', bound='IoPipelineMetadata')


##


class IoPipelineMessages(NamespaceClass):
    """Standard messages sent through a pipeline."""

    #

    class NeverInbound(Abstract):
        pass

    class NeverOutbound(Abstract):
        pass

    #

    class MayPropagate(Abstract):
        """
        These *may* be propagated all the way through the pipeline without being an error. These will be silently
        dropped when fed inbound and reaching the innermost pipeline position, but will still be emitted as pipeline
        output when fed outbound.
        """

    class MustPropagate(MayPropagate, Abstract):
        """
        These *must* be propagated all the way through the pipeline when sent in either direction. This is enforced via
        object identity - the same *instance* of the message must be seen at the end of the pipeline to be considered
        caught. This is intentional.
        """

    #

    class Pinning(Abstract):
        @property
        @abc.abstractmethod
        def pinned(self) -> ta.Optional[ta.Sequence['IoPipelineMessages.MustPropagate']]:
            raise NotImplementedError

    #

    @ta.final
    @dc.dataclass(frozen=True, eq=False)
    class InitialInput(NeverOutbound, MustPropagate):  # ~ Netty `ChannelInboundHandler::channelActive`
        """Signals that the inbound stream has begun producing input (`connected`)."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}@{id(self):x}()'

    @ta.final
    @dc.dataclass(frozen=True, eq=False)
    class FinalInput(NeverOutbound, MustPropagate):  # ~ Netty `ChannelInboundHandler::channelInactive`
        """Signals that the inbound stream has produced its final message (`eof`)."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}@{id(self):x}()'

    @ta.final
    @dc.dataclass(frozen=True, eq=False)
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

        direction: ta.Optional['IoPipelineDirection'] = None
        handler: ta.Optional['IoPipelineHandlerRef'] = None

    #

    class Completable(Abstract, ta.Generic[T]):
        # Management of completable state is implemented as 'hidden' / dynamic attributes to allow mixing in with
        # otherwise frozen dataclasses.

        # _completion_state: ta.Literal['pending', 'succeeded', 'failed'] = 'pending'
        # _completion_: _Completion

        @ta.final
        class _Completion:
            result: ta.Any
            exc: ta.Optional[BaseException]
            listeners: ta.Optional[ta.List[ta.Callable[[ta.Any], None]]] = None

        def is_done(self) -> bool:
            try:
                cps = self._completion_state  # type: ignore[attr-defined]
            except AttributeError:
                return False
            return cps != 'pending'

        def is_succeeded(self) -> bool:
            try:
                cps = self._completion_state  # type: ignore[attr-defined]
            except AttributeError:
                return False
            return cps == 'succeeded'

        def get_result(self) -> T:
            check.state(self._completion_state == 'succeeded')  # type: ignore[attr-defined]

            return self._completion_.result  # type: ignore[attr-defined]

        def is_failed(self) -> bool:
            try:
                cps = self._completion_state  # type: ignore[attr-defined]
            except AttributeError:
                return False
            return cps == 'failed'

        def get_exception(self) -> ta.Optional[BaseException]:
            check.state(self._completion_state == 'failed')  # type: ignore[attr-defined]

            return self._completion_.exc  # type: ignore[attr-defined]

        def _completion(self) -> _Completion:
            try:
                return self._completion_  # type: ignore[attr-defined]
            except AttributeError:
                pass

            cpl = IoPipelineMessages.Completable._Completion()  # noqa
            object.__setattr__(self, '_completion_', cpl)
            return cpl

        def add_listener(self, fn: ta.Callable[['IoPipelineMessages.Completable[T]'], None]) -> None:
            check.state(not self.is_done())

            cpl = self._completion()
            if (lst := cpl.listeners) is None:
                lst = cpl.listeners = []
            lst.append(fn)

        def set_succeeded(self, result: T) -> None:
            check.state(not self.is_done())

            object.__setattr__(self, '_completion_state', 'succeeded')

            try:
                cpl = self._completion_  # type: ignore[attr-defined]
            except AttributeError:
                return

            cpl.result = result
            if (lst := cpl.listeners) is not None:
                for fn in lst:
                    fn(self)

            object.__delattr__(self, '_completion_')

        def set_failed(self, exc: ta.Optional[BaseException] = None) -> None:
            check.state(not self.is_done())

            object.__setattr__(self, '_completion_state', 'failed')

            try:
                cpl = self._completion_  # type: ignore[attr-defined]
            except AttributeError:
                return

            cpl.exc = exc
            if (lst := cpl.listeners) is not None:
                for fn in lst:
                    fn(self)

            object.__delattr__(self, '_completion_')

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class Defer(NeverInbound, Pinning, Completable[T], ta.Generic[T]):
        fn: ta.Union[
            ta.Callable[['IoPipelineHandlerContext'], T],
            ta.Callable[[], T],
        ]

        no_context: bool = False

        def __repr__(self) -> str:
            return f'{type(self).__name__}@{id(self):x}({self.fn!r}{", no_context=True" if self.no_context else ""})'

        # _: dc.KW_ONLY

        _ctx: ta.Optional['IoPipelineHandlerContext'] = dc.field(default=None, repr=False)

        _pinned: ta.Optional[ta.Sequence['IoPipelineMessages.MustPropagate']] = dc.field(default=None, repr=False)

        @property
        def pinned(self) -> ta.Optional[ta.Sequence['IoPipelineMessages.MustPropagate']]:
            return self._pinned


##


class IoPipelineHandlerNotification(Abstract):  # ~ Netty `ChannelHandler` methods
    """
    Directionless, private events sent to a specific handler that are not to be forwarded to any other handler in either
    direction.
    """


class IoPipelineHandlerNotifications(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class Added(IoPipelineHandlerNotification):
        ctx: 'IoPipelineHandlerContext'

    @ta.final
    @dc.dataclass(frozen=True)
    class Removed(IoPipelineHandlerNotification):
        ctx: 'IoPipelineHandlerContext'


##


@ta.final
class IoPipelineHandlerRef(ta.Generic[T]):
    """
    Encapsulates a reference to a unique position of a handler instance in a pipeline, used at public api boundaries.

    Should the handler be removed from the relevant position in the pipeline, the ref instance becomes permanently
    invalidated.

    Note that this is definitionally identity hash/eq: given some valid ref, removing that ref from the pipeline and
    re-adding the same handler instance to the same effective position in a pipeline results in a different ref.
    """

    def __init__(self, *, _context: 'IoPipelineHandlerContext') -> None:
        self._context = _context

    @property
    def pipeline(self) -> 'IoPipeline':
        return self._context._pipeline  # noqa

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
            f'({self.handler!r})'  # {f"@{id(self.handler):x}"})'
        )


IoPipelineHandlerRef_ = IoPipelineHandlerRef['IoPipelineHandler']  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


##


@ta.final
class IoPipelineHandlerContext:
    """
    The embodiment of an instance of a handler at a position in a pipeline. Passed to IoPipelineHandler methods,
    providing handler-specific access to the pipeline. As instances of `ShareableIoPipelineHandler` may validly be
    simultaneously present at multiple positions in a pipeline, a single handler may have multiple active context
    instances associated with it in any given pipeline.

    Instances of this class are considered private to a handler instance and are not to be cached or shared in any way.
    The method names reflect this: they are operations available to the handler in the context of a pipeline processing
    operation.
    """

    def __init__(
            self,
            *,
            _pipeline: 'IoPipeline',
            _handler: 'IoPipelineHandler',

            _name: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._pipeline: ta.Final[IoPipeline] = _pipeline
        self._handler: ta.Final[IoPipelineHandler] = _handler

        self._name: ta.Final[ta.Optional[str]] = _name

        self._ref: IoPipelineHandlerRef_ = IoPipelineHandlerRef(_context=self)

        hty = type(_handler)
        self._handles_inbound = hty.inbound is not IoPipelineHandler.inbound
        self._handles_outbound = hty.outbound is not IoPipelineHandler.outbound

    _next_in: 'IoPipelineHandlerContext'  # 'next'
    _next_out: 'IoPipelineHandlerContext'  # 'prev'

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}@{id(self):x}'
            f'{"!INVALIDATED" if self._invalidated else ""}'
            f'{f"<{self._name!r}>" if self._name is not None else ""}'
            f'<pipeline@{id(self.pipeline):x}>'
            f'({self._handler!r})'  # @{id(self._handler):x})'
        )

    @property
    def ref(self) -> IoPipelineHandlerRef_:
        return self._ref

    @property
    def pipeline(self) -> 'IoPipeline':
        return self._pipeline

    @property
    def services(self) -> 'IoPipelineServices':  # noqa
        return self._pipeline._services  # noqa

    @property
    def handler(self) -> 'IoPipelineHandler':
        return self._handler

    @property
    def name(self) -> ta.Optional[str]:
        return self._name

    #

    def defer(
            self,
            fn: ta.Callable[['IoPipelineHandlerContext'], T],
            *,
            pin: ta.Optional[ta.Sequence[IoPipelineMessages.MustPropagate]] = None,
    ) -> IoPipelineMessages.Defer[T]:
        return self._pipeline._defer(self, fn, pin=pin)  # noqa

    def defer_no_context(
            self,
            fn: ta.Callable[[], T],
            *,
            pin: ta.Optional[ta.Sequence[IoPipelineMessages.MustPropagate]] = None,
    ) -> IoPipelineMessages.Defer[T]:
        return self._pipeline._defer(self, fn, no_context=True, pin=pin)  # noqa

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
            self.__dict: ta.Dict[IoPipelineHandlerContext.StorageKey, ta.Any] = {}

        @property
        def dict(self) -> ta.Dict['IoPipelineHandlerContext.StorageKey', ta.Any]:
            return self.__dict

        def __getitem__(self, key: 'IoPipelineHandlerContext.StorageKey[T]') -> T:
            return self.__dict[key]

        @ta.overload
        def get(
                self,
                key: 'IoPipelineHandlerContext.StorageKey[T]',
                default: T,
                /,
        ) -> T:
            ...

        @ta.overload
        def get(
                self,
                key: 'IoPipelineHandlerContext.StorageKey[T]',
                default: ta.Optional[T] = None,
                /,
        ) -> ta.Optional[T]:
            ...

        def get(self, key, default=None, /):
            return self.__dict.get(key, default)

        def __setitem__(self, key: 'IoPipelineHandlerContext.StorageKey[T]', value: T) -> None:
            self.__dict[key] = value

        def __delitem__(self, key: 'IoPipelineHandlerContext.StorageKey[T]') -> None:
            del self.__dict[key]

        def __len__(self) -> int:
            return len(self.__dict)

        def __contains__(self, key: 'IoPipelineHandlerContext.StorageKey[T]') -> bool:
            return key in self.__dict

        def __iter__(self) -> ta.Iterator['IoPipelineHandlerContext.StorageKey[T]']:
            return iter(self.__dict)

        def items(self) -> ta.Iterator[ta.Tuple['IoPipelineHandlerContext.StorageKey[T]', T]]:
            return iter(self.__dict.items())

    _storage_: Storage

    @property
    def storage(self) -> Storage:
        try:
            return self._storage_
        except AttributeError:
            pass
        self._storage_ = ret = IoPipelineHandlerContext.Storage()
        return ret

    #

    def _notify(self, no: IoPipelineHandlerNotification) -> None:
        check.isinstance(no, IoPipelineHandlerNotification)
        check.state(self._pipeline._execution_depth > 0)  # noqa

        self._handler.notify(self, no)

    ##
    # Feeding `type`'s is forbidden as it's almost always going to be an error - usually forgetting to instantiate a
    # marker dataclass)

    _FORBIDDEN_INBOUND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        IoPipelineMessages.NeverInbound,
        IoPipelineHandlerNotification,
        type,
        type(None),
    )

    def _inbound(self, msg: ta.Any) -> None:
        check.state(not self._invalidated, ContextInvalidatedIoPipelineError)
        check.state(self._pipeline._state == IoPipeline.State.READY and self._pipeline._execution_depth > 0)  # noqa

        check.not_isinstance(msg, self._FORBIDDEN_INBOUND_TYPES)

        if (mt := self._pipeline._message_tap) is not None:  # noqa
            mt(self, 'inbound', msg)

        if isinstance(msg, IoPipelineMessages.MustPropagate):
            self._pipeline._propagation.add_must(self, 'inbound', msg)  # noqa

        try:
            self._handler.inbound(self, msg)

        except self._pipeline._all_never_handle_exceptions:  # type: ignore[misc]  # noqa
            raise

        except BaseException as e:
            if self._handling_error or self._pipeline._config.raise_immediately:  # noqa
                raise
            self._handle_error(e, 'inbound')

    _FORBIDDEN_OUTBOUND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        IoPipelineMessages.NeverOutbound,
        IoPipelineHandlerNotification,
        type,
        type(None),
    )

    def _outbound(self, msg: ta.Any) -> None:
        check.state(not self._invalidated, ContextInvalidatedIoPipelineError)
        check.state(self._pipeline._state == IoPipeline.State.READY and self._pipeline._execution_depth > 0)  # noqa

        check.not_isinstance(msg, self._FORBIDDEN_OUTBOUND_TYPES)

        if (mt := self._pipeline._message_tap) is not None:  # noqa
            mt(self, 'outbound', msg)

        if isinstance(msg, IoPipelineMessages.MustPropagate):
            self._pipeline._propagation.add_must(self, 'outbound', msg)  # noqa

        try:
            self._handler.outbound(self, msg)

        except self._pipeline._all_never_handle_exceptions:  # type: ignore[misc]  # noqa
            raise

        except BaseException as e:
            if self._handling_error or self._pipeline._config.raise_immediately:  # noqa
                raise
            self._handle_error(e, 'outbound')

    #

    def _run_deferred(self, dfl: IoPipelineMessages.Defer) -> None:
        check.state(not self._invalidated, ContextInvalidatedIoPipelineError)
        check.state(self._pipeline._state == IoPipeline.State.READY and self._pipeline._execution_depth > 0)  # noqa

        check.state(dfl._ctx is self)  # noqa

        try:
            if dfl.no_context:
                res = dfl.fn()  # type: ignore[call-arg]
            else:
                res = dfl.fn(self)  # type: ignore[call-arg]

        except self._pipeline._all_never_handle_exceptions:  # type: ignore[misc]  # noqa
            raise

        except BaseException as e:  # noqa
            dfl.set_failed(e)

            if self._handling_error or self._pipeline._config.raise_immediately:  # noqa
                raise
            self._handle_error(e, 'inbound')

        else:
            dfl.set_succeeded(res)

    #

    _handling_error: bool = False

    def _handle_error(self, e: BaseException, direction: 'IoPipelineDirection') -> None:
        check.state(not self._handling_error)
        self._handling_error = True

        try:
            try:
                self.feed_in(IoPipelineMessages.Error(e, direction, self._ref))

            except self._pipeline._all_never_handle_exceptions:  # type: ignore[misc]  # noqa
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
                IoPipelineMessages.NeverInbound,
                IoPipelineHandlerNotification,
                type,
                None,
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
                IoPipelineMessages.NeverOutbound,
                IoPipelineHandlerNotification,
                type,
                None,
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
        self.feed_out(IoPipelineMessages.FinalOutput())

    #

    def mark_propagated(
            self,
            direction: 'IoPipelineDirection',
            msg: IoPipelineMessages.MustPropagate,
    ) -> None:
        self._pipeline._propagation.remove_must(self, direction, msg)  # noqa


##


class IoPipelineHandler(Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if not (
            cls.__hash__ is object.__hash__ and
            cls.__eq__ is object.__eq__ and
            cls.__ne__ is object.__ne__
        ):
            raise TypeError(
                f'IoPipelineHandler subclass {cls.__name__} must not override __hash__, __eq__ or __ne__',
            )

    #

    def notify(self, ctx: IoPipelineHandlerContext, no: IoPipelineHandlerNotification) -> None:
        pass

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_in(msg)

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_out(msg)


class ShareableIoPipelineHandler(IoPipelineHandler, Abstract):
    pass


##


IoPipelineDirection = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'inbound',
    'outbound',
]

IoPipelineDirectionOrDuplex = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    IoPipelineDirection,
    'duplex',
]

IoPipelineUpdate = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'added',
    'removed',
]

IoPipelineHandlerUpdate = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'adding',
    'added',
    'removing',
    'removed',
]


##


class IoPipelineService(Abstract):
    def pipeline_update(self, pipeline: 'IoPipeline', kind: IoPipelineUpdate) -> None:
        pass

    def handler_update(self, handler_ref: IoPipelineHandlerRef, kind: IoPipelineHandlerUpdate) -> None:
        pass

    def pipeline_enter(self, pipeline: 'IoPipeline') -> None:
        pass

    def pipeline_exit(self, pipeline: 'IoPipeline') -> None:
        pass


@ta.final
class IoPipelineServices:
    def __init__(self, lst: ta.Sequence[IoPipelineService]) -> None:
        self._lst = lst

        self._by_type_cache: ta.Dict[type, ta.Sequence[ta.Any]] = {}
        self._single_by_type_cache: ta.Dict[type, ta.Optional[ta.Any]] = {}

        self._handles_pipeline_update = handles_pipeline_update = []
        self._handles_handler_update = handles_handler_update = []
        self._handles_pipeline_enter = handles_pipeline_enter = []
        self._handles_pipeline_exit = handles_pipeline_exit = []

        for svc in lst:
            sty = type(svc)
            if sty.pipeline_update is not IoPipelineService.pipeline_update:
                handles_pipeline_update.append(sty)
            if sty.handler_update is not IoPipelineService.handler_update:
                handles_handler_update.append(sty)
            if sty.pipeline_enter is not IoPipelineService.pipeline_enter:
                handles_pipeline_enter.append(sty)
            if sty.pipeline_exit is not IoPipelineService.pipeline_exit:
                handles_pipeline_exit.append(sty)

    _handles_pipeline_update: ta.Sequence[IoPipelineService]
    _handles_handler_update: ta.Sequence[IoPipelineService]
    _handles_pipeline_enter: ta.Sequence[IoPipelineService]
    _handles_pipeline_exit: ta.Sequence[IoPipelineService]

    _EMPTY: ta.ClassVar['IoPipelineServices']

    @classmethod
    def of(cls, obj: ta.Union['IoPipelineServices', ta.Sequence[IoPipelineService]]) -> 'IoPipelineServices':  # noqa
        if isinstance(obj, cls):
            return obj
        elif not obj:
            return cls._EMPTY
        else:
            return cls(list(obj))

    def __len__(self) -> int:
        return len(self._lst)

    def __iter__(self) -> ta.Iterator[IoPipelineService]:
        return iter(self._lst)

    def __contains__(self, item: IoPipelineService) -> bool:
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


IoPipelineServices._EMPTY = IoPipelineServices([])  # noqa


##


class IoPipelineMetadata(Abstract):
    pass


@ta.final
class IoPipelineMetadatas:
    def __init__(self, lst: ta.Sequence[IoPipelineMetadata]) -> None:
        dct: ta.Dict[type, ta.Any] = {}
        for md in lst:
            mty = type(md)
            check.not_in(mty, dct)
            dct[mty] = md
        self._dct = dct

    _EMPTY: ta.ClassVar['IoPipelineMetadatas']

    @classmethod
    def of(cls, obj: ta.Union['IoPipelineMetadatas', ta.Sequence[IoPipelineMetadata]]) -> 'IoPipelineMetadatas':  # noqa
        if isinstance(obj, cls):
            return obj
        elif not obj:
            return cls._EMPTY
        else:
            return cls(list(obj))

    def __len__(self) -> int:
        return len(self._dct)

    def __contains__(self, ty: ta.Type[IoPipelineMetadata]) -> bool:
        return ty in self._dct

    def __iter__(self) -> ta.Iterator[IoPipelineMetadata]:
        return iter(self._dct.values())

    @dc.dataclass(frozen=True)
    class MetadataType(ta.Generic[IoPipelineMetadataT]):
        """This is entirely just a workaround for mypy's `type-abstract` deficiency."""

        ty: ta.Type[IoPipelineMetadataT]

    def __getitem__(
            self,
            ty: ta.Union[
                MetadataType[IoPipelineMetadataT],
                ta.Type[IoPipelineMetadataT],
            ],
    ) -> IoPipelineMetadataT:
        if isinstance(ty, self.MetadataType):
            ty = ty.ty

        return self._dct[ty]

    @ta.overload
    def get(
            self,
            ty: ta.Union[
                MetadataType[IoPipelineMetadataT],
                ta.Type[IoPipelineMetadataT],
            ],
            default: IoPipelineMetadataT,
            /,
    ) -> IoPipelineMetadataT:
        ...

    @ta.overload
    def get(
            self,
            ty: ta.Union[
                MetadataType[IoPipelineMetadataT],
                ta.Type[IoPipelineMetadataT],
            ],
            default: ta.Optional[IoPipelineMetadataT] = None,
            /,
    ) -> ta.Optional[IoPipelineMetadataT]:
        ...

    def get(self, ty, default=None, /):
        if isinstance(ty, self.MetadataType):
            ty = ty.ty

        return self._dct.get(ty, default)


IoPipelineMetadatas._EMPTY = IoPipelineMetadatas([])  # noqa


##


@ta.final
class _IoPipelinePropagation:
    @dc.dataclass()
    class _PendingMustEntry:
        msg: ta.Any
        direction: IoPipelineDirection
        last_seen: IoPipelineHandlerContext
        pinned_by: ta.Optional[IoPipelineMessages.Pinning] = None

    def __init__(self, p: 'IoPipeline') -> None:
        self._p = p

        if not self._p._config.disable_propagation_checking:  # noqa
            self._pending_must: ta.Final[ta.Dict[int, _IoPipelinePropagation._PendingMustEntry]] = {}

    def add_must(
            self,
            ctx: IoPipelineHandlerContext,
            direction: IoPipelineDirection,
            msg: IoPipelineMessages.MustPropagate,
    ) -> None:
        if self._p._config.disable_propagation_checking:  # noqa
            return

        i = id(msg)
        try:
            x = self._pending_must[i]
        except KeyError:
            self._pending_must[i] = _IoPipelinePropagation._PendingMustEntry(  # noqa
                msg,
                direction,
                ctx,
            )
            return

        check.is_(msg, x.msg)
        check.equal(direction, x.direction)
        check.state(x.pinned_by is None)
        x.last_seen = ctx

    def pin_musts(
            self,
            pinning: IoPipelineMessages.Pinning,
    ) -> None:
        if self._p._config.disable_propagation_checking or not (lst := pinning.pinned):  # noqa
            return

        for msg in lst:
            x = self._pending_must[id(msg)]
            check.none(x.pinned_by)
            x.pinned_by = pinning

    def unpin_musts(
            self,
            pinning: IoPipelineMessages.Pinning,
    ) -> None:
        if self._p._config.disable_propagation_checking or not (lst := pinning.pinned):  # noqa
            return

        for msg in lst:
            x = self._pending_must[id(msg)]
            check.is_(x.pinned_by, pinning)
            x.pinned_by = None

    def remove_must(
            self,
            ctx: IoPipelineHandlerContext,
            direction: IoPipelineDirection,
            msg: IoPipelineMessages.MustPropagate,
    ) -> None:
        if self._p._config.disable_propagation_checking:  # noqa
            return

        i = id(msg)
        try:
            x = self._pending_must.pop(i)
        except KeyError:
            raise MessageNotPropagatedIoPipelineError.new_single(
                direction,
                msg,
                last_seen=ctx._ref,  # noqa
            ) from None

        if (
                x.msg is not msg or
                x.direction != direction or
                x.pinned_by is not None
        ):
            raise MessageNotPropagatedIoPipelineError.new_single(
                direction,
                msg,
                last_seen=ctx._ref,  # noqa
            )

    def check_and_clear(self) -> None:
        if self._p._config.disable_propagation_checking:  # noqa
            return

        if not self._pending_must:
            return

        il: ta.List[ta.Tuple[ta.Any, ta.Any]] = []
        ol: ta.List[ta.Tuple[ta.Any, ta.Any]] = []

        for x in self._pending_must.values():
            if x.pinned_by is None:
                (il if x.direction == 'inbound' else ol).append((x.msg, x.last_seen._ref))  # noqa

        if not (il or ol):
            return

        e = MessageNotPropagatedIoPipelineError.new(
            inbound_with_last_seen=il,
            outbound_with_last_seen=ol,
        )

        for lst in (il, ol):
            for msg, _ in lst:
                del self._pending_must[id(msg)]

        raise e


##


IoPipelineMessageTap = ta.Callable[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    [
        IoPipelineHandlerContext,
        IoPipelineDirection,
        ta.Any,
    ],
    None,
]


IoPipelineMessageTapTuple = ta.Tuple[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    IoPipelineHandlerContext,
    IoPipelineDirection,
    ta.Any,
]


class ListIoPipelineMessageTap(ta.Sequence[IoPipelineMessageTapTuple]):
    def __init__(self, lst: ta.Optional[ta.List[IoPipelineMessageTapTuple]] = None) -> None:
        super().__init__()

        if lst is None:
            lst = []
        self.lst: ta.List[IoPipelineMessageTapTuple] = lst  # noqa

    def __iter__(self) -> ta.Iterator[IoPipelineMessageTapTuple]:
        return iter(self.lst)

    def __len__(self) -> int:
        return len(self.lst)

    def __getitem__(self, index):
        return self.lst[index]

    def __call__(
            self,
            ctx: IoPipelineHandlerContext,
            direction: IoPipelineDirection,
            msg: ta.Any,
    ) -> None:
        self.lst.append((ctx, direction, msg))


##


@ta.final
class IoPipeline:
    @ta.final
    @dc.dataclass(frozen=True)
    class Config:
        # TODO: 'close'? 'deadletter'? combination? composition? ...
        inbound_terminal: ta.Literal['drop', 'raise'] = 'raise'

        disable_propagation_checking: bool = False

        raise_immediately: bool = False

        def __post_init__(self) -> None:
            check.in_(self.inbound_terminal, ('drop', 'raise'))

        #

        def update(self, **kwargs: ta.Any) -> 'IoPipeline.Config':
            return dc.replace(self, **kwargs)

        DEFAULT: ta.ClassVar['IoPipeline.Config']

    Config.DEFAULT = Config()

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class Spec:
        # Initial handlers are optional - handlers may be freely added and removed later.
        handlers: ta.Sequence[IoPipelineHandler] = ()

        config: 'IoPipeline.Config' = dc.field(default_factory=lambda: IoPipeline.Config.DEFAULT)

        # _: dc.KW_ONLY

        # Metadata and ervices are fixed for the lifetime of the pipeline.
        metadata: ta.Union[ta.Sequence[IoPipelineMetadata], IoPipelineMetadatas] = ()
        services: ta.Union[ta.Sequence[IoPipelineService], IoPipelineServices] = ()

        #

        def update_config(self, **kwargs: ta.Any) -> 'IoPipeline.Spec':
            return dc.replace(self, config=self.config.update(**kwargs))

    @classmethod
    def new(
            cls,
            handlers: ta.Sequence[IoPipelineHandler] = (),
            config: 'IoPipeline.Config' = Config.DEFAULT,
            *,
            metadata: ta.Union[ta.Sequence[IoPipelineMetadata], IoPipelineMetadatas] = (),
            services: ta.Union[ta.Sequence[IoPipelineService], IoPipelineServices] = (),
    ) -> 'IoPipeline':
        return cls(IoPipeline.Spec(
            handlers=handlers,
            config=config,
            metadata=metadata,
            services=services,
        ))

    #

    def __init__(
            self,
            spec: Spec,
            *,
            never_handle_exceptions: ta.Tuple[type, ...] = (),
            message_tap: ta.Optional[IoPipelineMessageTap] = None,
    ) -> None:
        super().__init__()

        self._config: ta.Final[IoPipeline.Config] = spec.config
        self._never_handle_exceptions = never_handle_exceptions
        self._message_tap = message_tap

        self._metadata: ta.Final[IoPipelineMetadatas] = IoPipelineMetadatas.of(spec.metadata)
        self._services: ta.Final[IoPipelineServices] = IoPipelineServices.of(spec.services)

        #

        self._all_never_handle_exceptions: ta.Tuple[type, ...] = (
            UnhandleableIoPipelineError,
            *never_handle_exceptions,
        )

        self._propagation: _IoPipelinePropagation = _IoPipelinePropagation(self)

        #

        self._output: ta.Final[IoPipeline._Output] = IoPipeline._Output()

        #

        self._outermost = outermost = IoPipelineHandlerContext(
            _pipeline=self,
            _handler=IoPipeline._Outermost(),
        )
        self._innermost = innermost = IoPipelineHandlerContext(
            _pipeline=self,
            _handler=IoPipeline._Innermost(),
        )

        # Explicitly does not form a ring, iteration past the outermost/innermost is always an error and will
        # intentionally raise AttributeError if not caught earlier.
        outermost._next_in = innermost  # noqa
        innermost._next_out = outermost  # noqa

        self._unique_contexts: ta.Final[ta.Dict[IoPipelineHandler, IoPipelineHandlerContext]] = {}
        self._shareable_contexts: ta.Final[ta.Dict[ShareableIoPipelineHandler, ta.Set[IoPipelineHandlerContext]]] = {}  # noqa

        self._contexts_by_name: ta.Final[ta.Dict[str, IoPipelineHandlerContext]] = {}

        #

        self._state = IoPipeline.State.READY

        #

        try:
            for svc in self._services._handles_pipeline_update:  # noqa
                svc.pipeline_update(self, 'added')

            for h in spec.handlers:
                self.add_innermost(h)

        except self._all_never_handle_exceptions:  # type: ignore[misc]
            raise

        except BaseException:  # noqa
            self.destroy()
            raise

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    ##
    # state

    class State(enum.Enum):
        NEW = 'new'
        READY = 'ready'
        DESTROYING = 'destroying'
        DESTROYED = 'destroyed'

    _state: State = State.NEW

    @property
    def state(self) -> State:
        return self._state

    @property
    def is_ready(self) -> bool:
        return self._state is IoPipeline.State.READY

    #

    _saw_any_input = False
    _saw_initial_input = False
    _saw_final_input = False
    _saw_final_output = False

    @property
    def saw_any_input(self) -> bool:
        return self._saw_any_input

    @property
    def saw_initial_input(self) -> bool:
        return self._saw_initial_input

    @property
    def saw_final_input(self) -> bool:
        return self._saw_final_input  # Note: only 'pipeline-level'

    @property
    def saw_final_output(self) -> bool:
        return self._saw_final_output

    ##
    # sub-collections

    @property
    def metadata(self) -> IoPipelineMetadatas:
        return self._metadata

    @property
    def services(self) -> IoPipelineServices:
        return self._services

    ##
    # execution

    _execution_depth = 0

    def _step_in(self) -> None:
        self._execution_depth += 1

        if self._execution_depth == 1:
            for svc in self._services._handles_pipeline_enter:  # noqa
                svc.pipeline_enter(self)

    def _step_out(self) -> None:
        check.state(self._execution_depth > 0)

        self._execution_depth -= 1

        if not self._execution_depth:
            for svc in self._services._handles_pipeline_exit:  # noqa
                svc.pipeline_exit(self)

            self._propagation.check_and_clear()

    @ta.final
    class _EnterContextManager:
        def __init__(self, p: 'IoPipeline') -> None:
            self._p = p

        def __enter__(self) -> None:
            self._p._step_in()  # noqa

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            self._p._step_out()  # noqa

    def enter(self) -> ta.ContextManager[None]:
        return self._EnterContextManager(self)

    #

    def _notify(self, ctx: IoPipelineHandlerContext, no: IoPipelineHandlerNotification) -> None:
        self._step_in()
        try:
            ctx._notify(no)  # noqa

        finally:
            self._step_out()

    def notify(self, handler_ref: IoPipelineHandlerRef, no: IoPipelineHandlerNotification) -> None:
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self)  # noqa
        self._notify(ctx, no)

    #

    def _feed_in_to(self, ctx: IoPipelineHandlerContext, msgs: ta.Iterable[ta.Any]) -> None:
        self._step_in()
        try:
            for msg in msgs:
                if self._saw_final_input:
                    raise SawFinalInputIoPipelineError
                elif isinstance(msg, IoPipelineMessages.FinalInput):
                    self._saw_final_input = True

                if isinstance(msg, IoPipelineMessages.InitialInput):
                    if self._saw_any_input:
                        raise SawInitialInputIoPipelineError
                    check.state(not self._saw_initial_input)
                    self._saw_initial_input = True
                self._saw_any_input = True

                ctx._inbound(msg)  # noqa

        finally:
            self._step_out()

    def feed_in_to(self, handler_ref: IoPipelineHandlerRef, *msgs: ta.Any) -> None:
        # TODO: remove? internal only? used by replace-self pattern
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self)  # noqa
        self._feed_in_to(ctx, msgs)

    def feed_in(self, *msgs: ta.Any) -> None:
        self._feed_in_to(self._outermost, msgs)  # noqa

    def feed_initial_input(self) -> None:
        self._feed_in_to(self._outermost, (IoPipelineMessages.InitialInput(),))  # noqa

    def feed_final_input(self) -> None:
        self._feed_in_to(self._outermost, (IoPipelineMessages.FinalInput(),))  # noqa

    #

    def _defer(
            self,
            ctx: IoPipelineHandlerContext,
            fn: ta.Union[
                ta.Callable[[IoPipelineHandlerContext], T],
                ta.Callable[[], T],
            ],
            *,
            no_context: bool = False,
            pin: ta.Optional[ta.Sequence[IoPipelineMessages.MustPropagate]] = None,
    ) -> IoPipelineMessages.Defer[T]:
        check.is_(ctx._pipeline, self)  # noqa
        check.state(not ctx._invalidated)  # noqa

        dfl = IoPipelineMessages.Defer(
            fn,
            no_context,
            _ctx=ctx,
            _pinned=pin,
        )

        if pin:
            self._propagation.pin_musts(dfl)

        ctx.feed_out(dfl)

        return dfl

    def run_deferred(self, dfl: IoPipelineMessages.Defer) -> None:
        ctx = check.not_none(dfl._ctx)  # noqa
        check.is_(ctx._pipeline, self)  # noqa
        check.state(not ctx._invalidated)  # noqa

        self._step_in()
        try:
            if dfl._pinned:  # noqa
                self._propagation.unpin_musts(dfl)

            ctx._run_deferred(dfl)  # noqa

        finally:
            self._step_out()

    ##
    # output

    @ta.final
    class _Output:
        def __init__(self) -> None:
            self._q: ta.Final[collections.deque[ta.Any]] = collections.deque()

        def __repr__(self) -> str:
            return (
                f'{type(self).__qualname__}@{id(self):x}'
                f'<len={len(self._q)}>'
                '()'
            )

        def peek(self) -> ta.Optional[ta.Any]:
            if not self._q:
                return None

            return self._q[0]

        def poll(self) -> ta.Optional[ta.Any]:
            if not self._q:
                return None

            return self._q.popleft()

        def drain(self) -> ta.List[ta.Any]:
            out: ta.List[ta.Any] = []

            while self._q:
                out.append(self._q.popleft())

            return out

    @property
    def output(self) -> _Output:
        return self._output

    ##
    # handlers

    def _handler_update(self, ctx: IoPipelineHandlerContext, kind: IoPipelineHandlerUpdate) -> None:
        for svc in self._services._handles_handler_update:  # noqa
            svc.handler_update(ctx._ref, kind)  # noqa

    #

    def _terminal_inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:  # noqa
        if (tm := self._config.inbound_terminal) == 'drop':
            pass

        elif tm == 'raise':
            if not isinstance(msg, IoPipelineMessages.MayPropagate):
                raise MessageReachedTerminalIoPipelineError.new_single('inbound', msg)

        else:
            raise RuntimeError(f'unknown inbound terminal mode {tm}')

    def _terminal_outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:  # noqa
        if isinstance(msg, IoPipelineMessages.FinalOutput):
            self._saw_final_output = True
        elif self._saw_final_output:
            raise SawFinalOutputIoPipelineError

        self._output._q.append(msg)  # noqa

    #

    _outermost: ta.Final[IoPipelineHandlerContext]
    _innermost: ta.Final[IoPipelineHandlerContext]

    def _check_can_add(
            self,
            handler: IoPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> IoPipelineHandler:
        check.state(self._state == IoPipeline.State.READY)  # noqa

        if not isinstance(handler, ShareableIoPipelineHandler):
            check.not_in(handler, self._unique_contexts)

        if name is not None:
            check.not_in(name, self._contexts_by_name)

        return handler

    def _check_can_add_relative_to(self, ctx: IoPipelineHandlerContext) -> IoPipelineHandlerContext:
        check.is_(ctx._pipeline, self)  # noqa
        check.state(not ctx._invalidated)  # noqa

        return ctx

    def _add(
            self,
            handler: IoPipelineHandler,
            *,
            inner_to: ta.Optional[IoPipelineHandlerContext] = None,
            outer_to: ta.Optional[IoPipelineHandlerContext] = None,

            name: ta.Optional[str] = None,
    ) -> IoPipelineHandlerRef:
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

        ctx = IoPipelineHandlerContext(
            _pipeline=self,
            _handler=handler,

            _name=name,
        )

        self._handler_update(ctx, 'adding')  # noqa

        if isinstance(handler, ShareableIoPipelineHandler):
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

        self._handler_update(ctx, 'added')  # noqa

        # FIXME: exceptions?
        self._notify(ctx, IoPipelineHandlerNotifications.Added(ctx))

        return ctx._ref  # noqa

    def add_innermost(
            self,
            handler: IoPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> IoPipelineHandlerRef:
        return self._add(handler, outer_to=self._innermost, name=name)

    def add_outermost(
            self,
            handler: IoPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> IoPipelineHandlerRef:
        return self._add(handler, inner_to=self._outermost, name=name)

    def add_inner_to(
            self,
            inner_to: IoPipelineHandlerRef,
            handler: IoPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> IoPipelineHandlerRef:
        ctx = inner_to._context   # noqa
        return self._add(handler, inner_to=ctx, name=name)

    def add_outer_to(
            self,
            outer_to: IoPipelineHandlerRef,
            handler: IoPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> IoPipelineHandlerRef:
        ctx = outer_to._context   # noqa
        return self._add(handler, outer_to=ctx, name=name)

    #

    def _check_can_remove(self, handler_ref: IoPipelineHandlerRef) -> IoPipelineHandler:
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self)  # noqa

        check.state(self._state in (IoPipeline.State.READY, IoPipeline.State.DESTROYING))  # noqa

        check.state(not ctx._invalidated)  # noqa

        handler = ctx._handler  # noqa
        if isinstance(handler, ShareableIoPipelineHandler):
            check.in_(ctx, self._shareable_contexts[handler])
        else:
            check.equal(ctx, self._unique_contexts[handler])

        check.is_not(ctx, self._innermost)
        check.is_not(ctx, self._outermost)

        return handler

    def _remove(self, handler_ref: IoPipelineHandlerRef) -> None:
        self._check_can_remove(handler_ref)

        ctx = handler_ref._context  # noqa
        handler = ctx._handler  # noqa

        self._handler_update(ctx, 'removing')  # noqa

        if ctx._name is not None:  # noqa
            del self._contexts_by_name[ctx._name]  # noqa

        if isinstance(handler, ShareableIoPipelineHandler):
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

        self._handler_update(ctx, 'removed')  # noqa

        # FIXME: exceptions? defer?
        self._notify(ctx, IoPipelineHandlerNotifications.Removed(ctx))

    def remove(self, handler_ref: IoPipelineHandlerRef) -> None:
        self._remove(handler_ref)

    #

    def replace(
            self,
            old_handler_ref: IoPipelineHandlerRef,
            new_handler: IoPipelineHandler,
            *,
            name: ta.Optional[str] = None,
    ) -> IoPipelineHandlerRef:
        self._check_can_remove(old_handler_ref)
        self._check_can_add(new_handler, name=name)

        inner_to = old_handler_ref._context._next_out  # noqa
        self._remove(old_handler_ref)
        return self._add(new_handler, inner_to=inner_to, name=name)

    #

    @ta.final
    class _Outermost(IoPipelineHandler):
        """'Head' in Netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def outbound(self, ctx: 'IoPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, IoPipelineMessages.MustPropagate):
                ctx._pipeline._propagation.remove_must(ctx, 'outbound', msg)  # noqa

            ctx._pipeline._terminal_outbound(ctx, msg)  # noqa

    @ta.final
    class _Innermost(IoPipelineHandler):
        """'Tail' in Netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def inbound(self, ctx: 'IoPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, IoPipelineMessages.MustPropagate):
                ctx._pipeline._propagation.remove_must(ctx, 'inbound', msg)  # noqa

            ctx._pipeline._terminal_inbound(ctx, msg)  # noqa

    ##
    # caches

    @ta.final
    class _Caches:
        def __init__(self, p: 'IoPipeline') -> None:
            self._p = p

            self._handlers_by_type_cache: ta.Dict[type, ta.Sequence[IoPipelineHandlerRef]] = {}
            self._single_handlers_by_type_cache: ta.Dict[type, ta.Optional[IoPipelineHandlerRef]] = {}

        _handlers: ta.Sequence[IoPipelineHandlerRef_]

        def handlers(self) -> ta.Sequence[IoPipelineHandlerRef_]:
            try:
                return self._handlers
            except AttributeError:
                pass

            lst: ta.List[IoPipelineHandlerRef_] = []
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                lst.append(ctx._ref)  # noqa

            self._handlers = lst
            return lst

        _handlers_by_name: ta.Mapping[str, IoPipelineHandlerRef_]

        def handlers_by_name(self) -> ta.Mapping[str, IoPipelineHandlerRef_]:
            try:
                return self._handlers_by_name
            except AttributeError:
                pass

            dct: ta.Dict[str, IoPipelineHandlerRef_] = {}
            ctx = self._p._outermost  # noqa
            while (ctx := ctx._next_in) is not self._p._innermost:  # noqa
                if (n := ctx._name) is not None:  # noqa
                    dct[n] = ctx._ref  # noqa

            self._handlers_by_name = dct
            return dct

        def find_handlers_of_type(self, ty: ta.Type[T]) -> ta.Sequence[IoPipelineHandlerRef[T]]:
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

        def find_single_handler_of_type(self, ty: ta.Type[T]) -> ta.Optional[IoPipelineHandlerRef[T]]:
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
        self.__caches = caches = IoPipeline._Caches(self)
        return caches

    def _clear_caches(self) -> None:
        try:
            del self.__caches
        except AttributeError:
            pass

    def handlers(self) -> ta.Sequence[IoPipelineHandlerRef]:
        return self._caches().handlers()

    def handlers_by_name(self) -> ta.Mapping[str, IoPipelineHandlerRef_]:
        return self._caches().handlers_by_name()

    @dc.dataclass(frozen=True)
    class HandlerType(ta.Generic[T]):
        """This is entirely just a workaround for mypy's `type-abstract` deficiency."""

        ty: ta.Type[T]

    def find_handlers_of_type(
            self,
            ty: ta.Union[HandlerType[T], ta.Type[T]],
    ) -> ta.Sequence[IoPipelineHandlerRef[T]]:
        if isinstance(ty, IoPipeline.HandlerType):
            ty = ty.ty
        return self._caches().find_handlers_of_type(ty)

    def find_single_handler_of_type(
            self,
            ty: ta.Union[HandlerType[T], ta.Type[T]],
    ) -> ta.Optional[IoPipelineHandlerRef[T]]:
        if isinstance(ty, IoPipeline.HandlerType):
            ty = ty.ty
        return self._caches().find_single_handler_of_type(ty)

    #

    @ta.overload
    def find_handler(  # type: ignore[overload-overlap]
            self,
            handler: ShareableIoPipelineHandlerT,
    ) -> ta.Sequence[IoPipelineHandlerRef[ShareableIoPipelineHandlerT]]:
        ...

    @ta.overload
    def find_handler(
            self,
            handler: IoPipelineHandlerT,
    ) -> ta.Optional[IoPipelineHandlerRef[IoPipelineHandlerT]]:
        ...

    def find_handler(self, handler):
        if isinstance(handler, ShareableIoPipelineHandler):
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
    # destroy

    def __enter__(self) -> 'IoPipeline':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.destroy()

    def destroy(self) -> None:
        if self._state == IoPipeline.State.DESTROYED:
            return

        check.state(self._state == IoPipeline.State.READY)
        self._state = IoPipeline.State.DESTROYING

        self._step_in()
        try:
            im_ctx = self._innermost  # noqa
            om_ctx = self._outermost  # noqa
            while (ctx := im_ctx._next_out) is not om_ctx:  # noqa
                self.remove(ctx._ref)  # noqa

        finally:
            self._step_out()

        for svc in self._services._handles_pipeline_update:  # noqa
            svc.pipeline_update(self, 'removed')

        self._state = IoPipeline.State.DESTROYED
