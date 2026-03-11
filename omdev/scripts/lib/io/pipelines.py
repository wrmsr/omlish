#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../../../../omlish/io/pipelines/_amalg.py
# @omlish-git-diff-omit
# ruff: noqa: FURB188 PYI034 UP006 UP007 UP036 UP037 UP045 UP046
import abc
import asyncio
import collections
import collections.abc
import dataclasses as dc
import enum
import functools
import inspect
import io
import logging
import os.path
import sys
import threading
import time
import traceback
import types
import typing as ta


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


def __omlish_amalg__():  # noqa
    return dict(
        src_files=[
            dict(path='errors.py', sha1='2d8ee419a407c58dff224316695c9d90fe50f727'),
            dict(path='../streams/errors.py', sha1='67ca85fd8741b5bfefe76c872ce1c30c18fab06f'),
            dict(path='../../lite/abstract.py', sha1='a2fc3f3697fa8de5247761e9d554e70176f37aac'),
            dict(path='../../lite/asyncs.py', sha1='b3f2251c56617ce548abf9c333ac996b63edb23e'),
            dict(path='../../lite/check.py', sha1='d0fd2e52b4227fe590add3c567328c3c4cf5f199'),
            dict(path='../../lite/namespaces.py', sha1='27b12b6592403c010fb8b2a0af7c24238490d3a1'),
            dict(path='../../logs/levels.py', sha1='91405563d082a5eba874da82aac89d83ce7b6152'),
            dict(path='../../logs/warnings.py', sha1='c4eb694b24773351107fcc058f3620f1dbfb6799'),
            dict(path='core.py', sha1='3dabd48ce0e19fd974a89ea7b4dd2b6c4118d36b'),
            dict(path='../streams/types.py', sha1='8959d244de95eaf9f118cc3fd2d713d85e55ff36'),
            dict(path='../../logs/infos.py', sha1='4dd104bd468a8c438601dd0bbda619b47d2f1620'),
            dict(path='../../logs/metrics/base.py', sha1='95120732c745ceec5333f81553761ab6ff4bb3fb'),
            dict(path='../../logs/protocols.py', sha1='05ca4d1d7feb50c4e3b9f22ee371aa7bf4b3dbd1'),
            dict(path='asyncs.py', sha1='a78bd64bada44716809c19e95d6ca4a96f3a28d7'),
            dict(path='bytes/buffering.py', sha1='c19bddb05ef9449aa1a1c228901cab0d2d927946'),
            dict(path='drivers/metadata.py', sha1='44e49cb87136933ffe867087897eab5004034a93'),
            dict(path='flow/types.py', sha1='f6d06c7d6ca41a88930811507c966eeb073c15b3'),
            dict(path='handlers/fns.py', sha1='6dd1901ebdbdb31caeffab06d239f1c41e3f2726'),
            dict(path='handlers/queues.py', sha1='f49d19c5dd7de77299bedbfb3a77a36479fd1edf'),
            dict(path='sched/types.py', sha1='854b3f0f8ed5da2132a516f787b9019f5cb4eef5'),
            dict(path='../streams/base.py', sha1='bdeaff419684dec34fd0dc59808a9686131992bc'),
            dict(path='../streams/framing.py', sha1='dc2d7f638b042619fd3d95789c71532a29fd5fe4'),
            dict(path='../streams/utils.py', sha1='eb08fa1d56284b078f973eea6796747b9bbdffdf'),
            dict(path='../../logs/contexts.py', sha1='1000a6d5ddfb642865ca532e34b1d50759781cf0'),
            dict(path='../../logs/utils.py', sha1='9b879044cbdc3172fd7282c7f2a4880b81261cdd'),
            dict(path='bytes/queues.py', sha1='ea3b53a155622376836ba9e3499b85220f37b1fd'),
            dict(path='handlers/flatmap.py', sha1='7c9957c9e5136d1fa8ca51997914b4e9a5065843'),
            dict(path='../streams/direct.py', sha1='b01937212493e9a41644ac4e366e4cbab10332ce'),
            dict(path='../streams/scanning.py', sha1='00522802dff772689be66151430754d4f9706dbc'),
            dict(path='../../logs/base.py', sha1='eaa2ce213235815e2f86c50df6c41cfe26a43ba2'),
            dict(path='../../logs/std/records.py', sha1='67e552537d9268d4df6939b8a92be885fda35238'),
            dict(path='../streams/segmented.py', sha1='025cdf30e582a5a2b923e1859fbb4d3f367b811c'),
            dict(path='../../logs/asyncs.py', sha1='8376df395029a9d0957e2338adede895a9364215'),
            dict(path='../../logs/std/loggers.py', sha1='dbdfc66188e6accb75d03454e43221d3fba0f011'),
            dict(path='bytes/decoders.py', sha1='6f6d8bc1adc6a5277543389814bc26ef63e34561'),
            dict(path='../../logs/modules.py', sha1='dd7d5f8e63fe8829dfb49460f3929ab64b68ee14'),
            dict(path='drivers/asyncio.py', sha1='59e80c4ac127e727676f17e956783f3aa39b4088'),
            dict(path='_amalg.py', sha1='14b67747b1e3b3c1483050a7948a29888d732ed9'),
        ],
    )


########################################


# ../../lite/abstract.py
T = ta.TypeVar('T')

# ../../lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], ta.Type[Exception], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# ../../logs/levels.py
LogLevel = int  # ta.TypeAlias

# core.py
F = ta.TypeVar('F')
IoPipelineHandlerFn = ta.Callable[['IoPipelineHandlerContext', F], T]  # ta.TypeAlias
IoPipelineHandlerT = ta.TypeVar('IoPipelineHandlerT', bound='IoPipelineHandler')
ShareableIoPipelineHandlerT = ta.TypeVar('ShareableIoPipelineHandlerT', bound='ShareableIoPipelineHandler')  # noqa
IoPipelineMetadataT = ta.TypeVar('IoPipelineMetadataT', bound='IoPipelineMetadata')

# ../streams/types.py
BytesLike = ta.Union[bytes, bytearray, memoryview]  # ta.TypeAlias

# ../../logs/infos.py
LoggingMsgFn = ta.Callable[[], ta.Union[str, tuple]]  # ta.TypeAlias
LoggingExcInfoTuple = ta.Tuple[ta.Type[BaseException], BaseException, ta.Optional[types.TracebackType]]  # ta.TypeAlias
LoggingExcInfo = ta.Union[BaseException, LoggingExcInfoTuple]  # ta.TypeAlias
LoggingExcInfoArg = ta.Union[LoggingExcInfo, bool, None]  # ta.TypeAlias
LoggingContextInfo = ta.Any  # ta.TypeAlias

# ../streams/utils.py
CanByteStreamBuffer = ta.Union[BytesLike, 'ByteStreamBufferLike']  # ta.TypeAlias

# ../../logs/contexts.py
LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)


########################################
# ../errors.py


##


class IoPipelineError(Exception):
    pass


##


class UnhandleableIoPipelineError(IoPipelineError):
    pass


##
# state


class StateIoPipelineError(IoPipelineError):
    pass


class ContextInvalidatedIoPipelineError(StateIoPipelineError):
    pass


class SawInitialInputIoPipelineError(StateIoPipelineError):
    pass


class SawFinalInputIoPipelineError(StateIoPipelineError):
    pass


class SawFinalOutputIoPipelineError(StateIoPipelineError):
    pass


##
# messages


@dc.dataclass()
class MessageIoPipelineError(IoPipelineError):
    @ta.final
    @dc.dataclass(frozen=True)
    class Item:
        direction: ta.Literal['inbound', 'outbound']
        msg: ta.Any

        # _: dc.KW_ONLY

        last_seen: ta.Optional[ta.Any] = None

        def __repr__(self) -> str:
            return (
                f'{self.__class__.__name__}('
                f'{self.direction!r}'
                f', {self.msg!r}' +
                (f', last_seen={self.last_seen!r}' if self.last_seen is not None else '') +
                ')'
            )

    items: ta.Sequence[Item]

    @classmethod
    def new(
            cls,
            *,
            inbound: ta.Optional[ta.Sequence[ta.Any]] = None,
            inbound_with_last_seen: ta.Optional[ta.Sequence[ta.Tuple[ta.Any, ta.Any]]] = None,
            outbound: ta.Optional[ta.Sequence[ta.Any]] = None,
            outbound_with_last_seen: ta.Optional[ta.Sequence[ta.Tuple[ta.Any, ta.Any]]] = None,
    ) -> 'MessageIoPipelineError':
        items: ta.List[MessageIoPipelineError.Item] = []
        for msg in inbound or ():
            items.append(MessageIoPipelineError.Item('inbound', msg))
        for msg, last_seen in inbound_with_last_seen or ():
            items.append(MessageIoPipelineError.Item('inbound', msg, last_seen=last_seen))
        for msg in outbound or ():
            items.append(MessageIoPipelineError.Item('outbound', msg))
        for msg, last_seen in outbound_with_last_seen or ():
            items.append(MessageIoPipelineError.Item('outbound', msg, last_seen=last_seen))
        return cls(items)

    @classmethod
    def new_single(
            cls,
            direction: ta.Literal['inbound', 'outbound'],
            msg: ta.Any,
            *,
            last_seen: ta.Optional[ta.Any] = None,
    ) -> 'MessageIoPipelineError':
        return cls([
            MessageIoPipelineError.Item(
                direction,
                msg,
                last_seen=last_seen,
            ),
        ])

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.items!r})'


@dc.dataclass(repr=False)
class MessageNotPropagatedIoPipelineError(MessageIoPipelineError, UnhandleableIoPipelineError):
    pass


@dc.dataclass(repr=False)
class MessageReachedTerminalIoPipelineError(MessageIoPipelineError, UnhandleableIoPipelineError):
    pass


##
# misc (TODO: move/cleanup)


class DecodingIoPipelineError(IoPipelineError):
    pass


class IncompleteDecodingIoPipelineError(DecodingIoPipelineError):
    pass


class FlowControlValidationIoPipelineError(IoPipelineError):
    pass


########################################
# ../../streams/errors.py


##


class ByteStreamBufferError(Exception):
    pass


#


class NeedMoreDataByteStreamBufferError(ByteStreamBufferError):
    """
    Raised when an operation cannot complete because insufficient bytes are currently buffered.

    This is intentionally distinct from EOF: it means "try again after feeding more bytes".
    """


#


class LimitByteStreamBufferError(ValueError, ByteStreamBufferError):
    """
    Base class for buffer/framing limit violations.

    Subclasses inherit from ValueError so existing tests expecting ValueError continue to pass.
    """


class BufferTooLargeByteStreamBufferError(LimitByteStreamBufferError):
    """
    Buffered data exceeded a configured cap without finding a boundary that would allow progress.

    Typically indicates an unframed stream, a missing delimiter, or an upstream not enforcing limits.
    """


class FrameTooLargeByteStreamBufferError(LimitByteStreamBufferError):
    """A single decoded frame (payload before its boundary delimiter/length) exceeded a configured max size."""


#


class StateByteStreamBufferError(RuntimeError, ByteStreamBufferError):
    """
    Base class for invalid buffer state transitions (e.g., coalescing while a reservation is outstanding).

    Subclasses inherit from RuntimeError so existing tests expecting RuntimeError continue to pass.
    """


class OutstandingReserveByteStreamBufferError(StateByteStreamBufferError):
    """A reserve() is outstanding; an operation requiring stable storage cannot proceed."""


class NoOutstandingReserveByteStreamBufferError(StateByteStreamBufferError):
    """commit() was called without a preceding reserve()."""


########################################
# ../../../lite/abstract.py


##


_ABSTRACT_METHODS_ATTR = '__abstractmethods__'
_IS_ABSTRACT_METHOD_ATTR = '__isabstractmethod__'


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, _IS_ABSTRACT_METHOD_ATTR, False))


def compute_abstract_methods(cls: type) -> ta.FrozenSet[str]:
    # ~> https://github.com/python/cpython/blob/f3476c6507381ca860eec0989f53647b13517423/Modules/_abc.c#L358

    # Stage 1: direct abstract methods

    abstracts = {
        a
        # Get items as a list to avoid mutation issues during iteration
        for a, v in list(cls.__dict__.items())
        if is_abstract_method(v)
    }

    # Stage 2: inherited abstract methods

    for base in cls.__bases__:
        # Get __abstractmethods__ from base if it exists
        if (base_abstracts := getattr(base, _ABSTRACT_METHODS_ATTR, None)) is None:
            continue

        # Iterate over abstract methods in base
        for key in base_abstracts:
            # Check if this class has an attribute with this name
            try:
                value = getattr(cls, key)
            except AttributeError:
                # Attribute not found in this class, skip
                continue

            # Check if it's still abstract
            if is_abstract_method(value):
                abstracts.add(key)

    return frozenset(abstracts)


def update_abstracts(cls: ta.Type[T], *, force: bool = False) -> ta.Type[T]:
    if not force and not hasattr(cls, _ABSTRACT_METHODS_ATTR):
        # Per stdlib: We check for __abstractmethods__ here because cls might by a C implementation or a python
        # implementation (especially during testing), and we want to handle both cases.
        return cls

    abstracts = compute_abstract_methods(cls)
    setattr(cls, _ABSTRACT_METHODS_ATTR, abstracts)
    return cls


#


class AbstractTypeError(TypeError):
    pass


_FORCE_ABSTRACT_ATTR = '__forceabstract__'


class Abstract:
    """
    Different from, but interoperable with, abc.ABC / abc.ABCMeta:

     - This raises AbstractTypeError during class creation, not instance instantiation - unless Abstract or abc.ABC are
       explicitly present in the class's direct bases.
     - This will forbid instantiation of classes with Abstract in their direct bases even if there are no
       abstractmethods left on the class.
     - This is a mixin, not a metaclass.
     - As it is not an ABCMeta, this does not support virtual base classes. As a result, operations like `isinstance`
       and `issubclass` are ~7x faster.
     - It additionally enforces a base class order of (Abstract, abc.ABC) to preemptively prevent common mro conflicts.

    If not mixed-in with an ABCMeta, it will update __abstractmethods__ itself.
    """

    __slots__ = ()

    __abstractmethods__: ta.ClassVar[ta.FrozenSet[str]] = frozenset()

    #

    def __forceabstract__(self):
        raise TypeError

    # This is done manually, rather than through @abc.abstractmethod, to mask it from static analysis.
    setattr(__forceabstract__, _IS_ABSTRACT_METHOD_ATTR, True)

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        setattr(
            cls,
            _FORCE_ABSTRACT_ATTR,
            getattr(Abstract, _FORCE_ABSTRACT_ATTR) if Abstract in cls.__bases__ else False,
        )

        super().__init_subclass__(**kwargs)

        if not (Abstract in cls.__bases__ or abc.ABC in cls.__bases__):
            if ams := compute_abstract_methods(cls):
                amd = {
                    a: mcls
                    for mcls in cls.__mro__[::-1]
                    for a in ams
                    if a in mcls.__dict__
                }

                raise AbstractTypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: ' +
                    ', '.join(sorted([
                        '.'.join([
                            *([
                                *([m] if (m := getattr(c, '__module__')) else []),
                                getattr(c, '__qualname__', getattr(c, '__name__')),
                            ] if c is not None else '?'),
                            a,
                        ])
                        for a in ams
                        for c in [amd.get(a)]
                    ])),
                )

        xbi = (Abstract, abc.ABC)  # , ta.Generic ?
        bis = [(cls.__bases__.index(b), b) for b in xbi if b in cls.__bases__]
        if bis != sorted(bis):
            raise TypeError(
                f'Abstract subclass {cls.__name__} must have proper base class order of '
                f'({", ".join(getattr(b, "__name__") for b in xbi)}), got: '
                f'({", ".join(getattr(b, "__name__") for _, b in sorted(bis))})',
            )

        if not isinstance(cls, abc.ABCMeta):
            update_abstracts(cls, force=True)


########################################
# ../../../lite/asyncs.py


##


async def opt_await(aw: ta.Optional[ta.Awaitable[T]]) -> ta.Optional[T]:
    return (await aw if aw is not None else None)


async def async_list(ai: ta.AsyncIterable[T]) -> ta.List[T]:
    return [v async for v in ai]


async def async_enumerate(ai: ta.AsyncIterable[T]) -> ta.AsyncIterable[ta.Tuple[int, T]]:
    i = 0
    async for e in ai:
        yield (i, e)
        i += 1


##


def as_async(fn: ta.Callable[..., T], *, wrap: bool = False) -> ta.Callable[..., ta.Awaitable[T]]:
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return functools.wraps(fn)(inner) if wrap else inner


##


class SyncAwaitCoroutineNotTerminatedError(Exception):
    pass


def sync_await(aw: ta.Awaitable[T]) -> T:
    """
    Allows for the synchronous execution of async functions which will never actually *externally* await anything. These
    functions are allowed to await any number of other functions - including contextmanagers and generators - so long as
    nothing ever actually 'leaks' out of the function, presumably to an event loop.
    """

    ret = missing = object()

    async def thunk():
        nonlocal ret

        ret = await aw

    cr = thunk()
    try:
        try:
            cr.send(None)
        except StopIteration:
            pass

        if ret is missing or cr.cr_await is not None or cr.cr_running:
            raise SyncAwaitCoroutineNotTerminatedError('Not terminated')

    finally:
        cr.close()

    return ta.cast(T, ret)


#


def sync_aiter(ai: ta.AsyncIterator[T]) -> ta.Iterator[T]:
    while True:
        try:
            o = sync_await(ai.__anext__())
        except StopAsyncIteration:
            break
        yield o


def sync_async_list(ai: ta.AsyncIterable[T]) -> ta.List[T]:
    """
    Uses `sync_await` to synchronously read the full contents of a function call returning an async iterator, given that
    the function never externally awaits anything.
    """

    lst: ta.Optional[ta.List[T]] = None

    async def inner():
        nonlocal lst

        lst = [v async for v in ai]

    sync_await(inner())

    if not isinstance(lst, list):
        raise TypeError(lst)

    return lst


#


@ta.final
class SyncAwaitContextManager(ta.Generic[T]):
    def __init__(self, acm: ta.AsyncContextManager[T]) -> None:
        self._acm = acm

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._acm!r})'

    def __enter__(self) -> T:
        return sync_await(self._acm.__aenter__())

    def __exit__(self, exc_type, exc_val, exc_tb):
        return sync_await(self._acm.__aexit__(exc_type, exc_val, exc_tb))


sync_async_with = SyncAwaitContextManager


##


@ta.final
class SyncToAsyncContextManager(ta.Generic[T]):
    def __init__(self, cm: ta.ContextManager[T]) -> None:
        self._cm = cm

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._cm!r})'

    async def __aenter__(self) -> T:
        return self._cm.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback, /):
        return self._cm.__exit__(exc_type, exc_value, traceback)


as_async_context_manager = SyncToAsyncContextManager


########################################
# ../../../lite/check.py
"""
TODO:
 - def maybe(v: lang.Maybe[T])
 - def not_ ?
 - ** class @dataclass Raise - user message should be able to be an exception type or instance or factory
"""


##


class Checks:
    def __init__(self) -> None:
        super().__init__()

        self._config_lock = threading.RLock()
        self._on_raise_fns: ta.Sequence[CheckOnRaiseFn] = []
        self._exception_factory: CheckExceptionFactory = Checks.default_exception_factory
        self._args_renderer: ta.Optional[CheckArgsRenderer] = None
        self._late_configure_fns: ta.Sequence[CheckLateConfigureFn] = []

    @staticmethod
    def default_exception_factory(exc_cls: ta.Type[Exception], *args, **kwargs) -> Exception:
        return exc_cls(*args, **kwargs)  # noqa

    #

    def register_on_raise(self, fn: CheckOnRaiseFn) -> None:
        with self._config_lock:
            self._on_raise_fns = [*self._on_raise_fns, fn]

    def unregister_on_raise(self, fn: CheckOnRaiseFn) -> None:
        with self._config_lock:
            self._on_raise_fns = [e for e in self._on_raise_fns if e != fn]

    #

    def register_on_raise_breakpoint_if_env_var_set(self, key: str) -> None:
        import os

        def on_raise(exc: Exception) -> None:  # noqa
            if key in os.environ:
                breakpoint()  # noqa

        self.register_on_raise(on_raise)

    #

    def set_exception_factory(self, factory: CheckExceptionFactory) -> None:
        self._exception_factory = factory

    def set_args_renderer(self, renderer: ta.Optional[CheckArgsRenderer]) -> None:
        self._args_renderer = renderer

    #

    def register_late_configure(self, fn: CheckLateConfigureFn) -> None:
        with self._config_lock:
            self._late_configure_fns = [*self._late_configure_fns, fn]

    def _late_configure(self) -> None:
        if not self._late_configure_fns:
            return

        with self._config_lock:
            if not (lc := self._late_configure_fns):
                return

            for fn in lc:
                fn(self)

            self._late_configure_fns = []

    #

    class _ArgsKwargs:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def _raise(
            self,
            exception_type: ta.Type[Exception],
            default_message: str,
            message: CheckMessage,
            ak: _ArgsKwargs = _ArgsKwargs(),
            *,
            render_fmt: ta.Optional[str] = None,
    ) -> ta.NoReturn:
        self._late_configure()

        exc_args: tuple = ()

        if isinstance(message, type):
            exception_type = message

        else:
            message = default_message

            if callable(message):
                message = ta.cast(ta.Callable, message)(*ak.args, **ak.kwargs)
                if isinstance(message, tuple):
                    message, *exc_args = message  # type: ignore

            if message is None:
                message = default_message

            if render_fmt is not None and (af := self._args_renderer) is not None:
                rendered_args = af(render_fmt, *ak.args)
                if rendered_args is not None:
                    message = f'{message} : {rendered_args}'

            exc_args = (message, *exc_args)

        exc = self._exception_factory(
            exception_type,
            *exc_args,
            *ak.args,
            **ak.kwargs,
        )

        for fn in self._on_raise_fns:
            fn(exc)

        raise exc

    #

    def _unpack_isinstance_spec(self, spec: ta.Any) -> ta.Any:
        if spec == ta.Any:
            return object
        if spec is None:
            return None.__class__
        if not isinstance(spec, tuple):
            return spec
        if ta.Any in spec:
            return object
        if None in spec:
            spec = tuple(filter(None, spec)) + (None.__class__,)  # noqa
        return spec

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Type[T], msg: CheckMessage = None, /) -> T:
        ...

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Any:
        ...

    def isinstance(self, v, spec, msg=None):
        if not isinstance(v, spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)):  # noqa
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not isinstance(%s, %s)',
            )

        return v

    @ta.overload
    def of_isinstance(self, spec: ta.Type[T], msg: CheckMessage = None, /) -> ta.Callable[[ta.Any], T]:
        ...

    @ta.overload
    def of_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[ta.Any], ta.Any]:
        ...

    def of_isinstance(self, spec, msg=None, /):
        spec = spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)  # noqa

        def inner(v):
            return self.isinstance(v, spec, msg)

        return inner

    def cast(self, v: ta.Any, cls: ta.Type[T], msg: CheckMessage = None, /) -> T:
        if not isinstance(v, cls):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, cls),
            )

        return v

    def of_cast(self, cls: ta.Type[T], msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        def inner(v):
            return self.cast(v, cls, msg)

        return inner

    def not_isinstance(self, v: T, spec: ta.Any, msg: CheckMessage = None, /) -> T:  # noqa
        if isinstance(v, spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)):  # noqa
            self._raise(
                TypeError,
                'Must not be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='isinstance(%s, %s)',
            )

        return v

    def of_not_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        spec = spec if (st := type(spec)) is type or (st is tuple and all(type(x) is type for x in spec)) else self._unpack_isinstance_spec(spec)  # noqa

        def inner(v):
            return self.not_isinstance(v, spec, msg)

        return inner

    ##

    def issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None, /) -> ta.Type[T]:  # noqa
        if not issubclass(v, spec):
            self._raise(
                TypeError,
                'Must be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not issubclass(%s, %s)',
            )

        return v

    def not_issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None, /) -> ta.Type[T]:
        if issubclass(v, spec):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    def not_issubclass_except_nameerror(self, v: ta.Type[T], spec: ta.Callable[[], type], msg: CheckMessage = None, /) -> ta.Type[T]:  # noqa
        try:
            c = spec()
        except NameError:
            return v

        if issubclass(v, c):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    #

    def in_(self, v: T, c: ta.Container[T], msg: CheckMessage = None, /) -> T:
        if v not in c:
            self._raise(
                ValueError,
                'Must be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s not in %s',
            )

        return v

    def not_in(self, v: T, c: ta.Container[T], msg: CheckMessage = None, /) -> T:
        if v in c:
            self._raise(
                ValueError,
                'Must not be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s in %s',
            )

        return v

    def empty(self, v: SizedT, msg: CheckMessage = None, /) -> SizedT:
        if len(v) != 0:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def iterempty(self, v: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Iterable[T]:
        it = iter(v)
        try:
            next(it)
        except StopIteration:
            pass
        else:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def not_empty(self, v: SizedT, msg: CheckMessage = None, /) -> SizedT:
        if len(v) == 0:
            self._raise(
                ValueError,
                'Must not be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def unique(self, it: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Iterable[T]:
        dupes = [e for e, c in collections.Counter(it).items() if c > 1]
        if dupes:
            self._raise(
                ValueError,
                'Must be unique',
                msg,
                Checks._ArgsKwargs(it, dupes),
            )

        return it

    def single(self, obj: ta.Iterable[T], msg: CheckMessage = None, /) -> T:
        try:
            [value] = obj
        except ValueError:
            self._raise(
                ValueError,
                'Must be single',
                msg,
                Checks._ArgsKwargs(obj),
                render_fmt='%s',
            )

        return value

    def opt_single(self, obj: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Optional[T]:
        it = iter(obj)
        try:
            value = next(it)
        except StopIteration:
            return None

        try:
            next(it)
        except StopIteration:
            return value  # noqa

        self._raise(
            ValueError,
            'Must be empty or single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    async def async_single(self, obj: ta.AsyncIterable[T], msg: CheckMessage = None, /) -> T:
        ait = obj.__aiter__()

        try:
            try:
                value = await ait.__anext__()
            except StopAsyncIteration:
                pass

            else:
                try:
                    await ait.__anext__()
                except StopAsyncIteration:
                    return value

        finally:
            if inspect.isasyncgen(ait):
                await ait.aclose()

        self._raise(
            ValueError,
            'Must be single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    async def async_opt_single(self, obj: ta.AsyncIterable[T], msg: CheckMessage = None, /) -> ta.Optional[T]:
        ait = obj.__aiter__()

        try:
            try:
                value = await ait.__anext__()
            except StopAsyncIteration:
                return None

            try:
                await ait.__anext__()
            except StopAsyncIteration:
                return value  # noqa

        finally:
            if inspect.isasyncgen(ait):
                await ait.aclose()

        self._raise(
            ValueError,
            'Must be empty or single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    #

    def none(self, v: ta.Any, msg: CheckMessage = None, /) -> None:
        if v is not None:
            self._raise(
                ValueError,
                'Must be None',
                msg,
                render_fmt='%s',
            )

    def not_none(self, v: ta.Optional[T], msg: CheckMessage = None, /) -> T:
        if v is None:
            self._raise(
                ValueError,
                'Must not be None',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    #

    def equal(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o != v:
            self._raise(
                ValueError,
                'Must be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s != %s',
            )

        return v

    def not_equal(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o == v:
            self._raise(
                ValueError,
                'Must not be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s == %s',
            )

        return v

    def is_(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o is not v:
            self._raise(
                ValueError,
                'Must be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is not %s',
            )

        return v

    def is_not(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o is v:
            self._raise(
                ValueError,
                'Must not be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is %s',
            )

        return v

    def callable(self, v: T, msg: CheckMessage = None, /) -> T:  # noqa
        if not callable(v):
            self._raise(
                TypeError,
                'Must be callable',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def non_empty_str(self, v: ta.Optional[str], msg: CheckMessage = None, /) -> str:
        if not isinstance(v, str) or not v:
            self._raise(
                ValueError,
                'Must be non-empty str',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def replacing(self, expected: ta.Any, old: ta.Any, new: T, msg: CheckMessage = None, /) -> T:
        if old != expected:
            self._raise(
                ValueError,
                'Must be replacing',
                msg,
                Checks._ArgsKwargs(expected, old, new),
                render_fmt='%s -> %s -> %s',
            )

        return new

    def replacing_none(self, old: ta.Any, new: T, msg: CheckMessage = None, /) -> T:
        if old is not None:
            self._raise(
                ValueError,
                'Must be replacing None',
                msg,
                Checks._ArgsKwargs(old, new),
                render_fmt='%s -> %s',
            )

        return new

    #

    def arg(self, v: bool, msg: CheckMessage = None, /) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'Argument condition not met',
                msg,
                render_fmt='%s',
            )

    def state(self, v: bool, msg: CheckMessage = None, /) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'State condition not met',
                msg,
                render_fmt='%s',
            )


check = Checks()


########################################
# ../../../lite/namespaces.py


class NamespaceClass:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    def __init_subclass__(cls, **kwargs):  # noqa
        super().__init_subclass__(**kwargs)

        if any(issubclass(b, NamespaceClass) and b is not NamespaceClass for b in cls.__bases__):
            raise TypeError


########################################
# ../../../logs/levels.py


##


@ta.final
class NamedLogLevel(int):
    # logging.getLevelNamesMapping (or, as that is unavailable <3.11, logging._nameToLevel) includes the deprecated
    # aliases.
    _NAMES_BY_INT: ta.ClassVar[ta.Mapping[LogLevel, str]] = dict(sorted(logging._levelToName.items(), key=lambda t: -t[0]))  # noqa

    _INTS_BY_NAME: ta.ClassVar[ta.Mapping[str, LogLevel]] = {v: k for k, v in _NAMES_BY_INT.items()}

    _NAME_INT_PAIRS: ta.ClassVar[ta.Sequence[ta.Tuple[str, LogLevel]]] = list(_INTS_BY_NAME.items())

    #

    _CACHE: ta.ClassVar[ta.MutableMapping[int, 'NamedLogLevel']] = {}

    @ta.overload
    def __new__(cls, name: str, offset: int = 0, /) -> 'NamedLogLevel':
        ...

    @ta.overload
    def __new__(cls, i: int, /) -> 'NamedLogLevel':
        ...

    def __new__(cls, x, offset=0, /):
        if isinstance(x, str):
            return cls(cls._INTS_BY_NAME[x.upper()] + offset)
        elif not offset and (c := cls._CACHE.get(x)) is not None:
            return c
        else:
            return super().__new__(cls, x + offset)

    #

    _name_and_offset: ta.Tuple[str, int]

    @property
    def name_and_offset(self) -> ta.Tuple[str, int]:
        try:
            return self._name_and_offset
        except AttributeError:
            pass

        if (n := self._NAMES_BY_INT.get(self)) is not None:
            t = (n, 0)
        else:
            for n, i in self._NAME_INT_PAIRS:  # noqa
                if self >= i:
                    t = (n, (self - i))
                    break
            else:
                t = ('NOTSET', int(self))

        self._name_and_offset = t
        return t

    @property
    def exact_name(self) -> ta.Optional[str]:
        n, o = self.name_and_offset
        return n if not o else None

    @property
    def effective_name(self) -> str:
        n, _ = self.name_and_offset
        return n

    #

    def __str__(self) -> str:
        return self.exact_name or f'{self.effective_name}{int(self):+}'

    def __repr__(self) -> str:
        n, o = self.name_and_offset
        return f'{self.__class__.__name__}({n!r}{f", {int(o)}" if o else ""})'

    #

    CRITICAL: ta.ClassVar['NamedLogLevel']
    ERROR: ta.ClassVar['NamedLogLevel']
    WARNING: ta.ClassVar['NamedLogLevel']
    INFO: ta.ClassVar['NamedLogLevel']
    DEBUG: ta.ClassVar['NamedLogLevel']
    NOTSET: ta.ClassVar['NamedLogLevel']


NamedLogLevel.CRITICAL = NamedLogLevel(logging.CRITICAL)
NamedLogLevel.ERROR = NamedLogLevel(logging.ERROR)
NamedLogLevel.WARNING = NamedLogLevel(logging.WARNING)
NamedLogLevel.INFO = NamedLogLevel(logging.INFO)
NamedLogLevel.DEBUG = NamedLogLevel(logging.DEBUG)
NamedLogLevel.NOTSET = NamedLogLevel(logging.NOTSET)


NamedLogLevel._CACHE.update({i: NamedLogLevel(i) for i in NamedLogLevel._NAMES_BY_INT})  # noqa


########################################
# ../../../logs/warnings.py


##


class LoggingSetupWarning(Warning):
    pass


########################################
# ../core.py


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
    ) -> None:
        super().__init__()

        self._config: ta.Final[IoPipeline.Config] = spec.config
        self._never_handle_exceptions = never_handle_exceptions

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


########################################
# ../../streams/types.py


##


class ByteStreamBufferLike(Abstract):
    @ta.final
    def __bool__(self) -> bool:
        raise TypeError('Do not use bool() for ByteStreamBufferLike, use len().')

    @abc.abstractmethod
    def __len__(self) -> int:
        """
        Return the number of readable bytes.

        This is expected to be O(1). Many drivers and codecs use `len(buf)` in tight loops to decide whether more data
        is needed before attempting to parse a frame.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def peek(self) -> memoryview:
        """
        Return a contiguous, read-only `memoryview` of the first available bytes.

        This is the "next chunk" fast-path: for segmented views, the returned memoryview may represent only the first
        segment (and thus may be shorter than `len(self)`), but it must be non-copying. This is the fast-path for codecs
        that can parse headers from an initial contiguous region.

        The returned view should be treated as ephemeral: callers must assume it may be invalidated by subsequent buffer
        mutations (advance/write/reserve/commit), depending on the implementation.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def segments(self) -> ta.Sequence[memoryview]:
        """
        Return the readable contents as an ordered sequence of non-copying `memoryview` segments.

        This method is required because efficient operations in pure Python typically depend on delegating work to
        CPython's optimized implementations for searching/slicing within contiguous regions. By exposing
        already-contiguous segments, the buffer enables implementations of `find/rfind` and higher-level framing to
        avoid Python-level per-byte iteration.

        The returned segments must:
          - collectively represent exactly the readable bytes, in order
          - be 1-D, byte-oriented views (itemsize 1)
          - be non-copying views of the underlying storage
          - be non-empty - lack of data is represented by returning no segments, not empty segments

        Callers must assume that the returned views may be invalidated by subsequent mutations of the originating
        buffer/view (e.g., advancing, writing, reserving, committing), depending on the implementation's rules.
        """

        raise NotImplementedError


class ByteStreamBufferView(ByteStreamBufferLike, Abstract):
    """
    A read-only, possibly non-contiguous view of bytes.

    This is the result type of operations like `ByteStreamBuffer.split_to()`: it represents a *logical* byte sequence
    without requiring a copy. A `ByteStreamBufferView` is intentionally minimal: it is not a general-purpose container
    API, not a random-access sequence, and not intended for arbitrary indexing/slicing-heavy use.

    `ByteStreamBufferView` exists to make copy boundaries explicit:
      - Use `segments()` / `peek()` to access data without copying.
      - Use `tobytes()` (or `bytes(view)`) to intentionally materialize a contiguous `bytes` object.

    Implementations may be backed by one or many `memoryview` segments; the semantics are defined as if all readable
    bytes were concatenated in order.
    """

    @abc.abstractmethod
    def tobytes(self) -> bytes:
        """
        Materialize this view as a contiguous `bytes` object (copying).

        This is the explicit copy boundary: callers should prefer `peek()` / `segments()` for zero-copy-ish access when
        feasible, and use `tobytes()` only when a contiguous owned `bytes` is required.
        """

        raise NotImplementedError


class ByteStreamBuffer(ByteStreamBufferLike, Abstract):
    """
    An incremental, consumption-oriented byte accumulator intended for protocol parsing.

    A `ByteStreamBuffer` is a *stream buffer*: bytes are appended by a driver/transport and then consumed by codecs via
    peeking, searching, splitting, and advancing-without forcing repeated concatenation or reallocation. It is
    explicitly designed to support segmented storage (to avoid "a huge buffer pinned by a tiny tail") and to enable
    low-copy pipeline-style decoding (Netty/Tokio-inspired).

    What it is for:
      - buffering raw bytes between I/O and protocol codecs,
      - framing (delimiters/length-prefixed) using split/advance,
      - efficient searching over buffered bytes using C-accelerated primitives via `memoryview` segments.

    What it is *not* for:
      - a general-purpose replacement for `bytes`/`bytearray`,
      - a `collections.abc.Sequence` or random-access container abstraction,
      - arbitrary indexing/slicing-heavy workloads (use `bytes`/`bytearray`/`memoryview` directly).

    `ByteStreamBuffer` deliberately exposes `memoryview` at its boundary. This is foundational: it allows both immutable
    (`bytes`) and mutable (`bytearray`) internal storage to be viewed in O(1) without copying. It also avoids relying
    on `io.BytesIO` as a core backing store: while `BytesIO.getbuffer()` can expose a view, exported views pin the
    underlying buffer against resizing, which makes it awkward as a general-purpose buffer substrate.

    Semantics note:
      Many methods describe behavior in terms of the *conceptual concatenation* of readable bytes, even if the buffer
      is physically segmented. This is what "stream-correct" means here: results must be correct regardless of how the
      buffered bytes are chunked internally.
    """

    @abc.abstractmethod
    def advance(self, n: int, /) -> None:
        """
        Consume (discard) exactly `n` readable bytes from the front of the buffer.

        This operation must not copy remaining bytes unnecessarily. For segmented buffers, this typically adjusts a head
        offset and drops exhausted segments.

        Implementations must raise if `n` is negative or greater than `len(self)`.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def split_to(self, n: int, /) -> ByteStreamBufferView:
        """
        Split off and return a read-only view of the first `n` readable bytes, consuming them from this buffer.

        This is the core "low-copy framing" primitive:
          - codecs can `split_to(frame_len)` to obtain a view of an entire frame without copying,
          - then immediately continue parsing subsequent frames from the remaining bytes.

        Implementations should strive for O(1) or amortized O(1) behavior, returning a view that references underlying
        segments rather than materializing a new contiguous `bytes`.

        Implementations must raise if `n` is negative or greater than `len(self)`.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def coalesce(self, n: int, /) -> memoryview:
        """
        Ensure the first `n` readable bytes are available contiguously and return a view of them.

        Semantics:
          - Non-consuming: does not advance.
          - May restructure internal segments (content-preserving) to make the prefix contiguous.
          - Returns a read-only-ish `memoryview` (callers must not mutate readable bytes).

        Copying behavior:
          - If `peek()` already exposes >= n contiguous bytes, this is zero-copy.
          - Otherwise, it copies exactly the first `n` bytes into a new contiguous segment and rewrites the internal
            segment list so that segment[0] contains that prefix.

        Reserve interaction:
          - Disallowed while an outstanding reservation exists, since reserve() hands out a view that must not be
            invalidated by internal reshaping.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        """
        Find the first occurrence of `sub` within the readable bytes and return its offset, or -1 if not found.

        This operation is "stream-correct": it must behave as if searching within the conceptual concatenation of all
        readable bytes, even if the buffer is physically segmented. In particular, matches that span segment boundaries
        must be detected.

        `start` and `end` are offsets into the readable region, matching the semantics of `bytes.find()`:
          - `start` defaults to 0 (the beginning of readable bytes),
          - `end` defaults to `len(self)`.

        Rationale for being part of the core interface:
          In pure Python, higher-level codecs cannot efficiently implement correct cross-segment searching byte-by-byte.
          Keeping `find` near the owning storage allows implementations to exploit contiguous segments and CPython's
          optimized search within each segment while still providing correct stream semantics.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        """
        Find the last occurrence of `sub` within the readable bytes and return its offset, or -1 if not found.

        This operation is also stream-correct and matches `bytes.rfind()` semantics for `start`/`end`, interpreted as
        offsets into the readable region of this buffer.
        """

        raise NotImplementedError


class MutableByteStreamBuffer(ByteStreamBuffer, Abstract):
    """
    A writable `ByteStreamBuffer`: supports appending bytes and (optionally) reserving writable space.

    `MutableByteStreamBuffer` is the primary target for drivers/transports feeding data into protocol pipelines, and for
    encoders building outbound byte sequences. It intentionally does not imply any particular I/O model (blocking,
    asyncio, custom reactors); it is simply the mutable byte substrate.

    Implementations may be linear (single `bytearray` + indices), segmented (multiple chunks), or adaptive.
    """

    @property
    @abc.abstractmethod
    def max_size(self) -> ta.Optional[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def write(self, data: BytesLike, /) -> None:
        """
        Append `data` to the end of the readable region (after any existing unread bytes).

        Implementations should avoid needless copying; e.g., segmented buffers may store large `bytes` chunks directly,
        while linear buffers may copy into a `bytearray`.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def reserve(self, n: int, /) -> memoryview:
        """
        Reserve writable space for at least `n` bytes and return a writable `memoryview` into that space.

        This method exists to support "close to the metal" drivers that can fill buffers directly (e.g., `recv_into`,
        `readinto`) without allocating temporary `bytes` objects.

        The returned view represents capacity that is not yet part of the readable region. The caller must write into
        some prefix of the view and then call `commit(written)` to make those bytes readable.

        Implementations should document their rules regarding outstanding reservations; a simple and robust rule is:
          - only one active reservation may exist at a time,
          - mutations that would reallocate storage are forbidden while a reservation is outstanding.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def commit(self, n: int, /) -> None:
        """
        Commit `n` bytes from the most recent reservation, making them readable.

        Conceptually, `reserve()` may provide more capacity than the caller actually uses; `commit(n)` "shrinks" that
        over-reservation by only publishing the first `n` bytes as readable.

        Implementations must validate:
          - that a reservation is outstanding,
          - that `0 <= n <= reserved_length`.

        After commit, the reservation is considered consumed; subsequent reads and searches must include the committed
        bytes as part of the readable region.
        """

        raise NotImplementedError


########################################
# ../../../logs/infos.py
"""
TODO:
 - remove redundant info fields only present for std adaptation (Level.name, ...)
"""


##


def logging_context_info(cls):
    return cls


@ta.final
class LoggingContextInfos:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    @logging_context_info
    @ta.final
    class Name(ta.NamedTuple):
        name: str

    @logging_context_info
    @ta.final
    class Level(ta.NamedTuple):
        level: NamedLogLevel
        name: str

        @classmethod
        def build(cls, level: int) -> 'LoggingContextInfos.Level':
            nl: NamedLogLevel = level if level.__class__ is NamedLogLevel else NamedLogLevel(level)  # type: ignore[assignment]  # noqa
            return cls(
                level=nl,
                name=logging.getLevelName(nl),
            )

    @logging_context_info
    @ta.final
    class Msg(ta.NamedTuple):
        msg: str
        args: ta.Union[tuple, ta.Mapping[ta.Any, ta.Any], None]

        @classmethod
        def build(
                cls,
                msg: ta.Union[str, tuple, LoggingMsgFn],
                *args: ta.Any,
        ) -> 'LoggingContextInfos.Msg':
            s: str
            a: ta.Any

            if callable(msg):
                if args:
                    raise TypeError(f'Must not provide both a message function and args: {msg=} {args=}')
                x = msg()
                if isinstance(x, str):
                    s, a = x, ()
                elif isinstance(x, tuple):
                    if x:
                        s, a = x[0], x[1:]
                    else:
                        s, a = '', ()
                else:
                    raise TypeError(x)

            elif isinstance(msg, tuple):
                if args:
                    raise TypeError(f'Must not provide both a tuple message and args: {msg=} {args=}')
                if msg:
                    s, a = msg[0], msg[1:]
                else:
                    s, a = '', ()

            elif isinstance(msg, str):
                s, a = msg, args

            else:
                raise TypeError(msg)

            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L307  # noqa
            if a and len(a) == 1 and isinstance(a[0], collections.abc.Mapping) and a[0]:
                a = a[0]

            return cls(
                msg=s,
                args=a,
            )

    @logging_context_info
    @ta.final
    class Extra(ta.NamedTuple):
        extra: ta.Mapping[ta.Any, ta.Any]

    @logging_context_info
    @ta.final
    class Time(ta.NamedTuple):
        ns: int
        secs: float
        msecs: float
        relative_secs: float

        @classmethod
        def get_std_start_ns(cls) -> int:
            x: ta.Any = logging._startTime  # type: ignore[attr-defined]  # noqa

            # Before 3.13.0b1 this will be `time.time()`, a float of seconds. After that, it will be `time.time_ns()`,
            # an int.
            #
            # See:
            #  - https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            #
            if isinstance(x, float):
                return int(x * 1e9)
            else:
                return x

        @classmethod
        def build(
                cls,
                ns: int,
                *,
                start_ns: ta.Optional[int] = None,
        ) -> 'LoggingContextInfos.Time':
            # https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            secs = ns / 1e9  # ns to float seconds

            # Get the number of whole milliseconds (0-999) in the fractional part of seconds.
            # Eg: 1_677_903_920_999_998_503 ns --> 999_998_503 ns--> 999 ms
            # Convert to float by adding 0.0 for historical reasons. See gh-89047
            msecs = (ns % 1_000_000_000) // 1_000_000 + 0.0

            # https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
            if msecs == 999.0 and int(secs) != ns // 1_000_000_000:
                # ns -> sec conversion can round up, e.g:
                # 1_677_903_920_999_999_900 ns --> 1_677_903_921.0 sec
                msecs = 0.0

            if start_ns is None:
                start_ns = cls.get_std_start_ns()
            relative_secs = (ns - start_ns) / 1e6

            return cls(
                ns=ns,
                secs=secs,
                msecs=msecs,
                relative_secs=relative_secs,
            )

    @logging_context_info
    @ta.final
    class Exc(ta.NamedTuple):
        info: LoggingExcInfo
        info_tuple: LoggingExcInfoTuple

        @classmethod
        def build(
                cls,
                arg: LoggingExcInfoArg = False,
        ) -> ta.Optional['LoggingContextInfos.Exc']:
            if arg is True:
                sys_exc_info = sys.exc_info()
                if sys_exc_info[0] is not None:
                    arg = sys_exc_info
                else:
                    arg = None
            elif arg is False:
                arg = None
            if arg is None:
                return None

            info: LoggingExcInfo = arg
            if isinstance(info, BaseException):
                info_tuple: LoggingExcInfoTuple = (type(info), info, info.__traceback__)  # noqa
            else:
                info_tuple = info

            return cls(
                info=info,
                info_tuple=info_tuple,
            )

    @logging_context_info
    @ta.final
    class Caller(ta.NamedTuple):
        file_path: str
        line_no: int
        func_name: str
        stack_info: ta.Optional[str]

        @classmethod
        def is_internal_frame(cls, frame: types.FrameType) -> bool:
            file_path = os.path.normcase(frame.f_code.co_filename)

            # Yes, really.
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L204  # noqa
            # https://github.com/python/cpython/commit/5ca6d7469be53960843df39bb900e9c3359f127f
            if 'importlib' in file_path and '_bootstrap' in file_path:
                return True

            return False

        @classmethod
        def find_frame(cls, stack_offset: int = 0) -> ta.Optional[types.FrameType]:
            f: ta.Optional[types.FrameType] = sys._getframe(2 + stack_offset)  # noqa

            while f is not None:
                # NOTE: We don't check __file__ like stdlib since we may be running amalgamated - we rely on careful,
                # manual stack_offset management.
                if hasattr(f, 'f_code'):
                    return f

                f = f.f_back

            return None

        @classmethod
        def build(
                cls,
                stack_offset: int = 0,
                *,
                stack_info: bool = False,
        ) -> ta.Optional['LoggingContextInfos.Caller']:
            if (f := cls.find_frame(stack_offset + 1)) is None:
                return None

            # https://github.com/python/cpython/blob/08e9794517063c8cd92c48714071b1d3c60b71bd/Lib/logging/__init__.py#L1616-L1623  # noqa
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                sio.close()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]

            return cls(
                file_path=f.f_code.co_filename,
                line_no=f.f_lineno or 0,
                func_name=f.f_code.co_name,
                stack_info=sinfo,
            )

    @logging_context_info
    @ta.final
    class SourceFile(ta.NamedTuple):
        file_name: str
        module: str

        @classmethod
        def build(cls, caller_file_path: ta.Optional[str]) -> ta.Optional['LoggingContextInfos.SourceFile']:
            if caller_file_path is None:
                return None

            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L331-L336  # noqa
            try:
                file_name = os.path.basename(caller_file_path)
                module = os.path.splitext(file_name)[0]
            except (TypeError, ValueError, AttributeError):
                return None

            return cls(
                file_name=file_name,
                module=module,
            )

    @logging_context_info
    @ta.final
    class Thread(ta.NamedTuple):
        ident: int
        native_id: ta.Optional[int]
        name: str

        @classmethod
        def build(cls) -> 'LoggingContextInfos.Thread':
            return cls(
                ident=threading.get_ident(),
                native_id=threading.get_native_id() if hasattr(threading, 'get_native_id') else None,
                name=threading.current_thread().name,
            )

    @logging_context_info
    @ta.final
    class Process(ta.NamedTuple):
        pid: int

        @classmethod
        def build(cls) -> 'LoggingContextInfos.Process':
            return cls(
                pid=os.getpid(),
            )

    @logging_context_info
    @ta.final
    class Multiprocessing(ta.NamedTuple):
        process_name: str

        @classmethod
        def build(cls) -> ta.Optional['LoggingContextInfos.Multiprocessing']:
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L355-L364  # noqa
            if (mp := sys.modules.get('multiprocessing')) is None:
                return None

            return cls(
                process_name=mp.current_process().name,
            )

    @logging_context_info
    @ta.final
    class AsyncioTask(ta.NamedTuple):
        name: str

        @classmethod
        def build(cls) -> ta.Optional['LoggingContextInfos.AsyncioTask']:
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L372-L377  # noqa
            if (asyncio := sys.modules.get('asyncio')) is None:
                return None

            try:
                task = asyncio.current_task()
            except Exception:  # noqa
                return None

            if task is None:
                return None

            return cls(
                name=task.get_name(),  # Always non-None
            )


##


class UnexpectedLoggingStartTimeWarning(LoggingSetupWarning):
    pass


def _check_logging_start_time() -> None:
    if (x := LoggingContextInfos.Time.get_std_start_ns()) < (t := time.time()):
        import warnings  # noqa

        warnings.warn(
            f'Unexpected logging start time detected: '
            f'get_std_start_ns={x}, '
            f'time.time()={t}',
            UnexpectedLoggingStartTimeWarning,
        )


_check_logging_start_time()


########################################
# ../../../logs/metrics/base.py


##


class LoggerMetricUnit(Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            mut = LOGGER_METRIC_UNIT_TYPES
        except NameError:
            pass
        else:
            bcs = [bc for bc in mut if issubclass(cls, bc)]
            if len(bcs) != 1:
                raise TypeError(f'{cls.__name__} must be a subclass of exactly one of {mut}, got {bcs}.')

        try:
            mtc = LoggerMetric
        except NameError:
            pass
        else:
            if issubclass(cls, mtc):
                mp = cls.__mro__.index(mtc)
                mup = cls.__mro__.index(LoggerMetricUnit)
                if mup > mp:
                    raise TypeError(f'{cls.__name__} must have Metric before MetricUnit in its MRO.')


class CountLoggerMetricUnit(LoggerMetricUnit):
    @classmethod
    def default_value(cls) -> ta.Optional[float]:
        return 1


class RatioLoggerMetricUnit(LoggerMetricUnit):
    pass


class SecondsLoggerMetricUnit(LoggerMetricUnit):
    pass


class BytesLoggerMetricUnit(LoggerMetricUnit):
    pass


LOGGER_METRIC_UNIT_TYPES: ta.Tuple[ta.Type[LoggerMetricUnit], ...] = (
    CountLoggerMetricUnit,
    RatioLoggerMetricUnit,
    SecondsLoggerMetricUnit,
    BytesLoggerMetricUnit,
)


##


class LoggerMetricTag(Abstract):
    pass


##


class LoggerMetric(Abstract):
    @ta.final
    def __init__(self, value: ta.Optional[float] = None, *tags: LoggerMetricTag) -> None:
        if value is None:
            value = self.default_value()
        if value is None:
            raise ValueError(f'{type(self).__name__} has no default value.')

        self.__value = value
        self.__tags = tags

    @property
    def value(self) -> float:
        return self.__value

    @classmethod
    def default_value(cls) -> ta.Optional[float]:
        return None

    @property
    def tags(self) -> ta.Sequence[LoggerMetricTag]:
        return self.__tags

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r}, {", ".join(map(repr, self.tags))})'

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            mtt = LOGGER_METRIC_TYPES
        except NameError:
            pass
        else:
            bcs = [bc for bc in mtt if issubclass(cls, bc)]
            if Abstract in cls.__bases__:
                if len(bcs) > 1:
                    raise TypeError(f'{cls.__name__} must be a subclass of at most one of {mtt}, got {bcs}.')
            else:
                if len(bcs) != 1:
                    raise TypeError(f'{cls.__name__} must be a subclass of exactly one of {mtt}, got {bcs}.')

        # if Abstract not in cls.__bases__ and not issubclass(cls, LoggerMetricUnit):
        #     raise TypeError(f'{cls.__name__} must be a subclass of LoggerMetricUnit.')


class CounterLoggerMetric(CountLoggerMetricUnit, LoggerMetric, Abstract):
    pass


class GaugeLoggerMetric(LoggerMetric, Abstract):
    pass


class HistogramLoggerMetric(LoggerMetric, Abstract):
    pass


LOGGER_METRIC_TYPES: ta.Tuple[ta.Type[LoggerMetric], ...] = (
    CounterLoggerMetric,
    GaugeLoggerMetric,
    HistogramLoggerMetric,
)


##


class AnyLoggerMetricCollector(Abstract, ta.Generic[T]):
    @ta.final
    def metric(self, m: LoggerMetric) -> T:
        return self._metric(m)

    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> T:
        raise NotImplementedError


class LoggerMetricCollector(AnyLoggerMetricCollector[None], Abstract):
    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> None:
        raise NotImplementedError


class AsyncLoggerMetricCollector(AnyLoggerMetricCollector[ta.Awaitable[None]], Abstract):
    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AnyNopLoggerMetricCollector(AnyLoggerMetricCollector[T], Abstract):
    pass


class NopLoggerMetricCollector(AnyNopLoggerMetricCollector[None], LoggerMetricCollector):
    @ta.final
    def _metric(self, m: LoggerMetric) -> None:
        pass


class AsyncNopLoggerMetricCollector(AnyNopLoggerMetricCollector[ta.Awaitable[None]], AsyncLoggerMetricCollector):
    @ta.final
    async def _metric(self, m: LoggerMetric) -> None:
        pass


########################################
# ../../../logs/protocols.py


##


@ta.runtime_checkable
class LoggerLike(ta.Protocol):
    """Satisfied by both our Logger and stdlib logging.Logger."""

    def isEnabledFor(self, level: LogLevel) -> bool: ...  # noqa

    def getEffectiveLevel(self) -> LogLevel: ...  # noqa

    #

    def log(self, level: LogLevel, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def debug(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def info(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def warning(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def error(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def exception(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def critical(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa


########################################
# ../asyncs.py


##


class AsyncIoPipelineMessages(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class Await(
        IoPipelineMessages.Completable[T],
        IoPipelineMessages.NeverInbound,
        ta.Generic[T],
    ):
        obj: ta.Awaitable[T]


########################################
# ../bytes/buffering.py


##


class InboundBytesBufferingIoPipelineHandler(IoPipelineHandler, Abstract):
    @abc.abstractmethod
    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        """Returning `None` denotes currently unknown/unanswerable."""

        raise NotImplementedError


class OutboundBytesBufferingIoPipelineHandler(IoPipelineHandler, Abstract):
    @abc.abstractmethod
    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        """Returning `None` denotes currently unknown/unanswerable."""

        raise NotImplementedError


########################################
# ../drivers/metadata.py


##


@dc.dataclass(frozen=True)
class DriverIoPipelineMetadata(IoPipelineMetadata):
    driver: ta.Any


########################################
# ../flow/types.py


##


class IoPipelineFlowMessages(NamespaceClass):
    """
    Note: these inbound messages will never be sent without a `IoPipelineFlow` instance in `channel.services` -
    thus it's safe to refer to `ctx.services[IoPipelineFlow]` when handling these.
    """

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushInput(  # ~ Netty `ChannelInboundInvoker::fireChannelReadComplete`  # noqa
        IoPipelineMessages.MayPropagate,
        IoPipelineMessages.NeverOutbound,
    ):
        pass

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushOutput(  # ~ Netty 'ChannelOutboundInvoker::flush'
        IoPipelineMessages.MayPropagate,
        IoPipelineMessages.NeverInbound,
    ):
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForInput(  # ~ Netty `ChannelOutboundInvoker::read`
        IoPipelineMessages.MayPropagate,
        IoPipelineMessages.NeverInbound,
    ):
        pass

    #

    # # TODO:
    # @ta.final
    # @dc.dataclass(frozen=True)
    # class ReadyForOutput(  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
    #     IoPipelineMessages.MayPropagate,
    #     IoPipelineMessages.NeverOutbound,
    # ):
    #     pass

    # # TODO:
    # @ta.final
    # @dc.dataclass(frozen=True)
    # class PauseOutput(  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
    #     IoPipelineMessages.MayPropagate,
    #     IoPipelineMessages.NeverOutbound,
    # ):
    #     pass


##


class IoPipelineFlow(Abstract):
    @abc.abstractmethod
    def is_auto_read(
            self: ta.Union[
                'IoPipelineFlow',
                IoPipeline,
                IoPipelineHandlerContext,
                None,
            ],
    ) -> bool:
        # This strange construct grants the ability to do `IoPipelineFlow.is_auto_read(opt_flow)`, which is becoming
        # increasingly frequently useful in real code.
        if self is None:
            return False

        if isinstance(self, IoPipelineFlow):
            return self.is_auto_read()

        if isinstance(self, IoPipelineHandlerContext):
            self = self._pipeline  # noqa

        if isinstance(self, IoPipeline):
            return (fc := self.services.find(IoPipelineFlow)) is None or fc.is_auto_read()

        raise TypeError(self)


########################################
# ../handlers/fns.py


##


class IoPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class NoContext(ta.Generic[F, T]):
        fn: ta.Callable[[F], T]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, obj: F) -> T:
            return self.fn(obj)

    @classmethod
    def no_context(cls, fn: ta.Callable[[F], T]) -> IoPipelineHandlerFn[F, T]:
        return cls.NoContext(fn)

    #

    @dc.dataclass(frozen=True)
    class And:
        fns: ta.Sequence[IoPipelineHandlerFn[ta.Any, bool]]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
            return all(fn(ctx, msg) for fn in self.fns)

    @classmethod
    def and_(cls, *fns: IoPipelineHandlerFn[ta.Any, bool]) -> IoPipelineHandlerFn[ta.Any, bool]:
        if len(fns) == 1:
            return fns[0]
        return cls.And(fns)

    #

    @dc.dataclass(frozen=True)
    class Or:
        fns: ta.Sequence[IoPipelineHandlerFn[ta.Any, bool]]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
            return any(fn(ctx, msg) for fn in self.fns)

    @classmethod
    def or_(cls, *fns: IoPipelineHandlerFn[ta.Any, bool]) -> IoPipelineHandlerFn[ta.Any, bool]:
        if len(fns) == 1:
            return fns[0]
        return cls.Or(fns)

    #

    @dc.dataclass(frozen=True)
    class Not:
        fn: IoPipelineHandlerFn[ta.Any, bool]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
            return not self.fn(ctx, msg)

    @classmethod
    def not_(cls, fn: IoPipelineHandlerFn[ta.Any, bool]) -> IoPipelineHandlerFn[ta.Any, bool]:
        if isinstance(fn, cls.Not):
            return fn.fn
        return cls.Not(fn)

    #

    @dc.dataclass(frozen=True)
    class IsInstance:
        ty: ta.Union[type, ta.Tuple[type, ...]]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.ty!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
            return isinstance(msg, self.ty)

    @classmethod
    def isinstance(cls, ty: ta.Union[type, ta.Tuple[type, ...]]) -> IoPipelineHandlerFn[ta.Any, bool]:
        return cls.IsInstance(ty)

    @classmethod
    def not_isinstance(cls, ty: ta.Union[type, ta.Tuple[type, ...]]) -> IoPipelineHandlerFn[ta.Any, bool]:
        return cls.Not(cls.IsInstance(ty))


##


class FnIoPipelineHandler(IoPipelineHandler, Abstract):
    @classmethod
    def of(
            cls,
            *,
            inbound: ta.Optional[IoPipelineHandlerFn[ta.Any, None]] = None,
            outbound: ta.Optional[IoPipelineHandlerFn[ta.Any, None]] = None,
    ) -> IoPipelineHandler:
        if inbound is not None and outbound is not None:
            return DuplexFnIoPipelineHandler(inbound=inbound, outbound=outbound)
        elif inbound is not None:
            return InboundFnIoPipelineHandler(inbound)
        elif outbound is not None:
            return OutboundFnIoPipelineHandler(outbound)
        else:
            raise ValueError('At least one of inbound or outbound must be specified')


class InboundFnIoPipelineHandler(FnIoPipelineHandler):
    def __init__(self, inbound: IoPipelineHandlerFn[ta.Any, None]) -> None:
        super().__init__()

        self._inbound = inbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({self._inbound!r})'

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._inbound(ctx, msg)


class OutboundFnIoPipelineHandler(FnIoPipelineHandler):
    def __init__(self, outbound: IoPipelineHandlerFn[ta.Any, None]) -> None:
        super().__init__()

        self._outbound = outbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({self._outbound!r})'

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._outbound(ctx, msg)


class DuplexFnIoPipelineHandler(FnIoPipelineHandler):
    def __init__(
            self,
            *,
            inbound: IoPipelineHandlerFn[ta.Any, None],
            outbound: IoPipelineHandlerFn[ta.Any, None],
    ) -> None:
        super().__init__()

        self._inbound = inbound
        self._outbound = outbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}(inbound={self._inbound!r}, outbound={self._outbound!r})'

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._inbound(ctx, msg)

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._outbound(ctx, msg)


########################################
# ../handlers/queues.py
"""
TODO:
 - max size, simple backpressure?
"""


##


class QueueIoPipelineHandler(IoPipelineHandler, Abstract):
    def __init__(
            self,
            *,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            passthrough: ta.Union[bool, ta.Literal['must_propagate']] = 'must_propagate',
    ) -> None:
        super().__init__()

        self._filter = filter
        self._filter_type = filter_type
        self._passthrough = passthrough

        self._q: collections.deque[ta.Any] = collections.deque()

    def __repr__(self) -> str:
        return ''.join([
            f'{type(self).__name__}@{id(self):x}',
            f'<len={len(self._q)}>',
            '(',
            ', '.join([
                *([f'filter={self._filter!r}'] if self._filter is not None else []),
                *([f'filter_type={self._filter_type!r}'] if self._filter_type is not None else []),
                *([f'passthrough={self._passthrough!r}'] if self._passthrough else []),
            ]),
            ')',
        ])

    #

    def _append(self, msg: ta.Any) -> None:
        self._q.append(msg)

    def _popleft(self) -> ta.Any:
        return self._q.popleft()

    def poll(self) -> ta.Optional[ta.Any]:
        if not self._q:
            return None

        return self._popleft()

    def drain(self) -> ta.List[ta.Any]:
        out: ta.List[ta.Any] = []

        while self._q:
            out.append(self._popleft())

        return out

    #

    def _should_enqueue(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
        if self._filter is not None and not self._filter(ctx, msg):
            return False

        if self._filter_type is not None and not isinstance(msg, self._filter_type):
            return False

        return True

    def _should_passthrough(self, msg: ta.Any) -> bool:
        if isinstance(pt := self._passthrough, bool):
            return pt

        elif pt == 'must_propagate':
            return isinstance(msg, IoPipelineMessages.MustPropagate)

        else:
            raise RuntimeError(f'Unknown passthrough mode {self._passthrough!r} for {self!r}')

    def _handle(self, ctx: IoPipelineHandlerContext, msg: ta.Any, feed: ta.Callable[[ta.Any], None]) -> None:
        if not self._should_enqueue(ctx, msg):
            feed(msg)
            return

        self._append(msg)

        if self._should_passthrough(msg):
            feed(msg)


class InboundQueueIoPipelineHandler(QueueIoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, msg, ctx.feed_in)


class OutboundQueueIoPipelineHandler(QueueIoPipelineHandler):
    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, msg, ctx.feed_out)


class DuplexQueueIoPipelineHandler(
    InboundQueueIoPipelineHandler,
    OutboundQueueIoPipelineHandler,
):
    pass


########################################
# ../sched/types.py


##


class IoPipelineScheduling(Abstract):
    class Handle(Abstract):
        @abc.abstractmethod
        def cancel(self) -> None:
            raise NotImplementedError

    @abc.abstractmethod
    def schedule(
            self,
            handler_ref: IoPipelineHandlerRef,
            delay_s: float,
            fn: ta.Callable[[], None],
    ) -> Handle:
        raise NotImplementedError

    @abc.abstractmethod
    def cancel_all(self, handler_ref: ta.Optional[IoPipelineHandlerRef] = None) -> None:
        raise NotImplementedError


########################################
# ../../streams/base.py


##


class BaseByteStreamBufferLike(ByteStreamBufferLike, Abstract):
    def _norm_slice(self, start: int, end: ta.Optional[int]) -> ta.Tuple[int, int]:
        s, e, _ = slice(start, end, 1).indices(len(self))
        return (s, s) if e < s else (s, e)


########################################
# ../../streams/framing.py


##


class LongestMatchDelimiterByteStreamFrameDecoder:
    """
    A delimiter-based framing codec that supports *overlapping* delimiters with longest-match semantics.

    This is intentionally decoupled from any I/O model: it operates purely on a `ByteStreamBuffer`-like object
    (providing `__len__`, `find`, `split_to`, `advance`, and `segments`/`peek`).

    Key property:
      Given overlapping delimiters like [b'\\r', b'\\r\\n'], this codec will *not* emit a frame ending at '\\r' unless
      it can prove the next byte is not '\\n' (or the stream is finalized).

    Implementation note:
      This codec relies on `ByteStreamBuffer.find(...)` being stream-correct and C-accelerated over the buffer's
      underlying contiguous segments. In pure Python it is usually better to keep searching near the storage layer than
      to re-implement scanning byte-by-byte in higher-level codecs.

    Pairs well with `ScanningByteStreamBuffer`.
    """

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        dl = list(delims)
        if not dl:
            raise ValueError('no delimiters')
        if any(not isinstance(d, (bytes, bytearray)) for d in dl):
            raise TypeError(delims)
        if any(not d for d in dl):
            raise ValueError('empty delimiter')

        self._delims = tuple(bytes(d) for d in dl)
        self._keep_ends = keep_ends
        self._max_size = max_size

        # Sort by length descending for "choose longest at same start".
        self._delims_by_len = tuple(sorted(self._delims, key=len, reverse=True))

        # Build prefix relationships for overlap deferral. For each short delimiter, store longer delimiters that start
        # with it.
        pref: ta.Dict[bytes, ta.List[bytes]] = {}
        for d in self._delims:
            for e in self._delims:
                if d is e:
                    continue
                if len(e) > len(d) and e.startswith(d):
                    pref.setdefault(d, []).append(e)
        for k, vs in list(pref.items()):
            pref[k] = sorted(vs, key=len, reverse=True)
        self._prefix_longer = pref

        self._max_delim_len = max(len(d) for d in self._delims)

    @ta.overload
    def decode(
            self,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
            include_delims: ta.Literal[True],
    ) -> ta.List[ta.Tuple[ByteStreamBufferView, bytes]]:
        ...

    @ta.overload
    def decode(
            self,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
            include_delims: ta.Literal[False] = False,
    ) -> ta.List[ByteStreamBufferView]:
        ...

    def decode(
            self,
            buf,
            *,
            final=False,
            include_delims=False,
    ):
        """
        Consume as many complete frames as possible from `buf` and return them as views.

        - Frames are produced without copying (via `buf.split_to(...)`) when possible.
        - The delimiter is consumed from the buffer; it may be retained on the frame if `keep_ends=True`.
        - If `final=True`, the codec will not defer on overlapping delimiter prefixes at the end of the buffer.

        Raises:
          - BufferTooLargeByteStreamBufferError if no delimiter is present and the buffered prefix exceeds max_size.
          - FrameTooLargeByteStreamBufferError if the next frame payload (bytes before delimiter) exceeds max_size.

        Note on `max_size`:
          `max_size` is enforced as a limit on the *current* frame (bytes before the next delimiter). If the buffer
          contains bytes for a subsequent frame that already exceed `max_size`, this codec will only raise when it would
          otherwise need to make progress on that oversized frame. Concretely: if this call already emitted at least one
          frame, it will return those frames rather than raising immediately on trailing oversized data, leaving the
          remaining bytes buffered.
        """

        out: ta.List[ta.Any] = []

        while True:
            hit = self._find_next_delim(buf)
            if hit is None:
                if self._max_size is not None and len(buf) > self._max_size and not out:
                    raise BufferTooLargeByteStreamBufferError('buffer exceeded max_size without delimiter')
                return out

            pos, delim = hit

            if self._max_size is not None and pos > self._max_size:
                raise FrameTooLargeByteStreamBufferError('frame exceeded max_size')

            if not final and self._should_defer(buf, pos, delim):
                return out

            if self._keep_ends:
                frame = buf.split_to(pos + len(delim))
            else:
                frame = buf.split_to(pos)
                buf.advance(len(delim))

            if include_delims:
                out.append((frame, delim))
            else:
                out.append(frame)

    def _find_next_delim(self, buf: ByteStreamBuffer) -> ta.Optional[ta.Tuple[int, bytes]]:
        """
        Return (pos, delim) for the earliest delimiter occurrence. If multiple delimiters occur at the same position,
        choose the longest matching delimiter.
        """

        ln = len(buf)
        if not ln:
            return None

        best_pos = None  # type: ta.Optional[int]
        best_delim = None  # type: ta.Optional[bytes]

        # First pass: find the earliest position of any delimiter (cheap, uses buf.find).
        for d in self._delims:
            i = buf.find(d, 0, None)
            if i == -1:
                continue
            if best_pos is None or i < best_pos:
                best_pos = i
                best_delim = d
                if not best_pos:
                    # Can't beat position 0; still need to choose longest at this position.
                    pass
            elif i == best_pos and best_delim is not None and len(d) > len(best_delim):
                best_delim = d

        if best_pos is None or best_delim is None:
            return None

        # Second pass: at that position, choose the longest delimiter that actually matches there. (We can't just rely
        # on "which delimiter found it first" when overlaps exist.)
        pos = best_pos
        for d in self._delims_by_len:
            if pos + len(d) > ln:
                continue
            if buf.find(d, pos, pos + len(d)) == pos:
                return pos, d

        # Shouldn't happen: best_pos came from some delimiter occurrence.
        return pos, best_delim

    def _should_defer(self, buf: ByteStreamBuffer, pos: int, matched: bytes) -> bool:
        """
        Return True if we must defer because a longer delimiter could still match starting at `pos` but we don't yet
        have enough bytes to decide.

        We only defer when:
          - the current match ends at the end of the currently buffered bytes, and
          - there exists some longer delimiter that has `matched` as a prefix, and
          - the buffered bytes from pos match the available prefix of that longer delimiter.
        """

        ln = len(buf)
        endpos = pos + len(matched)
        if endpos != ln:
            return False

        longer = self._prefix_longer.get(matched)
        if not longer:
            return False

        avail = ln - pos
        for d2 in longer:
            if avail >= len(d2):
                # If we had enough bytes, we'd have matched d2 in _find_next_delim.
                continue
            # Check whether buffered bytes match the prefix of d2 that we have available.
            # Use stream-correct find on the prefix.
            prefix = d2[:avail]
            if buf.find(prefix, pos, pos + avail) == pos:
                return True

        return False


##


class LengthFieldByteStreamFrameDecoder:
    """
    Decode length-prefixed frames from a BytesBuffer/MutableBytesBuffer.

    This is modeled after the common Netty pattern:
      total_frame_length = length_field_value + length_adjustment + length_field_end_offset
    where:
      length_field_end_offset = length_field_offset + length_field_length

    Parameters:
      - length_field_offset: byte offset of the length field from the start of the frame
      - length_field_length: length of the length field in bytes (1, 2, 4, or 8)
      - byteorder: 'big' or 'little'
      - length_adjustment: adjustment added to computed frame length (may be negative)
      - initial_bytes_to_strip: number of leading bytes to drop from the emitted frame (typically used to strip the
        length field and/or header from the delivered payload)
      - max_frame_length: maximum allowed total frame length (before stripping)

    Notes:
      - This decoder operates directly on the provided buffer and consumes bytes as frames are produced.
      - It relies on `buf.coalesce(n)` for efficient header parsing in pure Python.
      - It does not require async/await and is suitable for pipeline-style codecs.
    """

    def __init__(
            self,
            *,
            length_field_offset: int = 0,
            length_field_length: int = 4,
            byteorder: ta.Literal['little', 'big'] = 'big',
            length_adjustment: int = 0,
            initial_bytes_to_strip: int = 0,
            max_frame_length: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        if length_field_offset < 0:
            raise ValueError(length_field_offset)
        if length_field_length not in (1, 2, 4, 8):
            raise ValueError(length_field_length)
        if byteorder not in ('big', 'little'):
            raise ValueError(byteorder)
        if initial_bytes_to_strip < 0:
            raise ValueError(initial_bytes_to_strip)
        if max_frame_length is not None and max_frame_length < 0:
            raise ValueError(max_frame_length)

        self._off = int(length_field_offset)
        self._llen = int(length_field_length)
        self._byteorder = byteorder
        self._adj = int(length_adjustment)
        self._strip = int(initial_bytes_to_strip)
        self._max = None if max_frame_length is None else int(max_frame_length)

        self._end_off = self._off + self._llen

    def decode(self, buf: ByteStreamBuffer) -> ta.List[ByteStreamBufferView]:
        """
        Consume as many complete frames as possible from `buf` and return them as views.

        Returns:
          - list of BytesView-like objects (from `split_to`) representing each decoded frame

        Raises:
          - FrameTooLarge if a frame exceeds max_frame_length
          - BufferTooLarge if max_frame_length is set and the buffered unread prefix grows beyond it without making
            progress (defensive; rarely hit if upstream caps buffer growth)
        """

        out: ta.List[ta.Any] = []

        while True:
            # Need at least enough bytes to read the length field.
            if len(buf) < self._end_off:
                return out

            # Read header up through the length field contiguously.
            # IMPORTANT: don't keep exported memoryviews alive across buffer mutation.
            mv = buf.coalesce(self._end_off)
            if len(mv) < self._end_off:
                # Defensive: coalesce contract.
                return out

            # Copy just the length field bytes (1/2/4/8) so we can safely mutate the buffer afterward.
            lf_bytes = bytes(mv[self._off:self._end_off])
            # del mv

            length_val = int.from_bytes(lf_bytes, self._byteorder, signed=False)

            total_len = length_val + self._adj + self._end_off
            if total_len < 0:
                raise ValueError('negative frame length')

            if self._max is not None and total_len > self._max:
                raise FrameTooLargeByteStreamBufferError('frame exceeded max_frame_length')

            # If we don't have the full frame yet, either wait or (optionally) fail fast if buffering is clearly out of
            # control.
            if len(buf) < total_len:
                if self._max is not None and len(buf) > self._max:
                    raise BufferTooLargeByteStreamBufferError(
                        'buffer exceeded max_frame_length without completing a frame',
                    )
                return out

            # We have a complete frame available.
            if self._strip:
                if self._strip > total_len:
                    raise ValueError('initial_bytes_to_strip > frame length')
                buf.advance(self._strip)
                total_len -= self._strip

            out.append(buf.split_to(total_len))

            # Loop for additional frames


########################################
# ../../streams/utils.py


##


class ByteStreamBuffers(NamespaceClass):
    _BYTES_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        bytes,
        bytearray,
    )

    _BYTES_LIKE_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        *_BYTES_TYPES,
        memoryview,
    )

    _CAN_CONVERT_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        *_BYTES_LIKE_TYPES,
        ByteStreamBufferLike,
    )

    #

    @classmethod
    def can_bytes(cls, obj: ta.Any, /) -> bool:
        return type(obj) in (cts := cls._CAN_CONVERT_TYPES) or isinstance(obj, cts)

    #

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[True],
            or_none: ta.Literal[True],
    ) -> ta.Optional[bytes]:
        ...

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[True],
            or_none: ta.Literal[False] = False,
    ) -> bytes:
        ...

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[False] = False,
            or_none: ta.Literal[True],
    ) -> ta.Union[bytes, bytearray, None]:
        ...

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[False] = False,
            or_none: ta.Literal[False] = False,
    ) -> ta.Union[bytes, bytearray]:
        ...

    @classmethod
    def to_bytes(
            cls,
            obj,
            /, *,
            strict=False,
            or_none=False,
    ):
        """
        Returns a non-shared version of the given object. If a possibly shared memoryview is acceptable, use
        `iter_segments`.
        """

        if strict:
            if (ot := type(obj)) is bytes or isinstance(obj, bytes):
                return obj

            elif ot is bytearray:
                return bytes(obj)

            elif isinstance(obj, memoryview):
                return cls.memoryview_to_bytes_strict(obj)

        else:
            if (ot := type(obj)) is bytes or ot is bytearray or isinstance(obj, cls._BYTES_TYPES):
                return obj

            elif isinstance(obj, memoryview):
                return cls.memoryview_to_bytes(obj)

        if isinstance(obj, ByteStreamBufferView):
            return obj.tobytes()

        elif isinstance(obj, ByteStreamBufferLike):
            return b''.join(bytes(mv) for mv in obj.segments())

        elif or_none:
            return None

        else:
            raise TypeError(obj)

    #

    @classmethod
    @ta.overload
    def bytes_len(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Optional[int]:
        ...

    @classmethod
    @ta.overload
    def bytes_len(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> int:
        ...

    @classmethod
    def bytes_len(cls, obj, or_none=False):
        if cls.can_bytes(obj):
            return len(obj)

        elif or_none:
            return None

        else:
            raise TypeError(obj)

    #

    @staticmethod
    def iter_segments(obj: ta.Any, /) -> ta.Iterator[memoryview]:
        if (ot := type(obj)) is memoryview:
            yield obj
        elif ot is bytes or ot is bytearray:
            yield memoryview(obj)

        elif isinstance(obj, memoryview):
            yield obj
        elif isinstance(obj, (bytes, bytearray)):
            yield memoryview(obj)

        elif isinstance(obj, ByteStreamBufferLike):
            yield from obj.segments()

        else:
            raise TypeError(obj)

    #

    @staticmethod
    def split(buf: ByteStreamBuffer, sep: bytes, /, *, final: bool = False) -> ta.List[ByteStreamBufferView]:
        out: ta.List[ByteStreamBufferView] = []
        while (i := buf.find(sep)) >= 0:
            out.append(buf.split_to(i + 1))
        if final and len(buf):
            out.append(buf.split_to(len(buf)))
        return out

    #

    @classmethod
    def memoryview_to_bytes(cls, mv: memoryview, /) -> ta.Union[bytes, bytearray]:
        if (((ot := type(obj := mv.obj)) is bytes or ot is bytearray or isinstance(obj, cls._BYTES_TYPES)) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
            return obj  # type: ignore[return-value]

        return mv.tobytes()

    @staticmethod
    def memoryview_to_bytes_strict(mv: memoryview, /) -> bytes:
        if (((ot := type(obj := mv.obj)) is bytes or isinstance(obj, bytes)) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
            return obj  # type: ignore[return-value]

        return mv.tobytes()


########################################
# ../../../logs/contexts.py


##


class LoggingContext(Abstract):
    @abc.abstractmethod
    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        raise NotImplementedError

    @ta.final
    def __getitem__(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self.get_info(ty)

    @ta.final
    def must_get_info(self, ty: ta.Type[LoggingContextInfoT]) -> LoggingContextInfoT:
        if (info := self.get_info(ty)) is None:
            raise TypeError(f'LoggingContextInfo absent: {ty}')
        return info


@ta.final
class SimpleLoggingContext(LoggingContext):
    def __init__(self, *infos: LoggingContextInfo) -> None:
        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {type(i): i for i in infos}

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)


##


class CaptureLoggingContext(LoggingContext, Abstract):
    @abc.abstractmethod
    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContext':
        raise NotImplementedError

    #

    class AlreadyCapturedError(Exception):
        pass

    class NotCapturedError(Exception):
        pass

    @abc.abstractmethod
    def capture(self) -> None:
        """Must be cooperatively called only from the expected locations."""

        raise NotImplementedError


@ta.final
class CaptureLoggingContextImpl(CaptureLoggingContext):
    @ta.final
    class NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    #

    def __init__(
            self,
            level: LogLevel,
            *,
            time_ns: ta.Optional[int] = None,

            exc_info: LoggingExcInfoArg = False,

            caller: ta.Union[LoggingContextInfos.Caller, ta.Type[NOT_SET], None] = NOT_SET,
            stack_offset: int = 0,
            stack_info: bool = False,
    ) -> None:
        if time_ns is None:
            time_ns = time.time_ns()

        # Done early to not trample on sys.exc_info()
        exc = LoggingContextInfos.Exc.build(exc_info)

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {}
        self._set_info(
            LoggingContextInfos.Level.build(level),
            exc,
            LoggingContextInfos.Time.build(time_ns),
        )

        if caller is not CaptureLoggingContextImpl.NOT_SET:
            self._infos[LoggingContextInfos.Caller] = caller
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

    def _set_info(self, *infos: ta.Optional[LoggingContextInfo]) -> 'CaptureLoggingContextImpl':
        for info in infos:
            if info is not None:
                self._infos[type(info)] = info
        return self

    def get_infos(self) -> ta.Mapping[ta.Type[LoggingContextInfo], LoggingContextInfo]:
        return self._infos

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)

    ##

    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContextImpl':
        return self._set_info(
            LoggingContextInfos.Name(name),
            LoggingContextInfos.Msg.build(msg, *args),
        )

    ##

    _stack_offset: int
    _stack_info: bool

    def inc_stack_offset(self, ofs: int = 1) -> 'CaptureLoggingContextImpl':
        if hasattr(self, '_stack_offset'):
            self._stack_offset += ofs
        return self

    _has_captured: bool = False

    def capture(self) -> None:
        if self._has_captured:
            raise CaptureLoggingContextImpl.AlreadyCapturedError
        self._has_captured = True

        if LoggingContextInfos.Caller not in self._infos:
            self._set_info(LoggingContextInfos.Caller.build(
                self._stack_offset + 1,
                stack_info=self._stack_info,
            ))

        if (caller := self[LoggingContextInfos.Caller]) is not None:
            self._set_info(LoggingContextInfos.SourceFile.build(
                caller.file_path,
            ))

        self._set_info(
            LoggingContextInfos.Thread.build(),
            LoggingContextInfos.Process.build(),
            LoggingContextInfos.Multiprocessing.build(),
            LoggingContextInfos.AsyncioTask.build(),
        )


########################################
# ../../../logs/utils.py


##


def exception_logging(log, exc_cls=Exception):  # noqa
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exc_cls as e:  # noqa
                log.exception('Error in %r', fn)
                raise

        return inner

    return outer


def async_exception_logging(alog, exc_cls=Exception):  # noqa
    def outer(fn):
        @functools.wraps(fn)
        async def inner(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except exc_cls as e:  # noqa
                await alog.exception('Error in %r', fn)
                raise

        return inner

    return outer


##


class LogTimingContext:
    DEFAULT_LOG: ta.ClassVar[ta.Optional[LoggerLike]] = None

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def __init__(
            self,
            description: str,
            *,
            log: ta.Union[LoggerLike, ta.Type[_NOT_SPECIFIED], None] = _NOT_SPECIFIED,  # noqa
            level: int = logging.DEBUG,
    ) -> None:
        super().__init__()

        self._description = description
        if log is self._NOT_SPECIFIED:
            log = self.DEFAULT_LOG  # noqa
        self._log: ta.Optional[LoggerLike] = log  # type: ignore
        self._level = level

    def set_description(self, description: str) -> 'LogTimingContext':
        self._description = description
        return self

    _begin_time: float
    _end_time: float

    def __enter__(self) -> 'LogTimingContext':
        self._begin_time = time.time()

        if self._log is not None:
            self._log.log(self._level, f'Begin : {self._description}')  # noqa

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.time()

        if self._log is not None:
            self._log.log(
                self._level,
                f'End : {self._description} - {self._end_time - self._begin_time:0.2f} s elapsed',
            )


log_timing_context = LogTimingContext


########################################
# ../bytes/queues.py


##


class InboundBytesBufferingQueueIoPipelineHandler(
    InboundBytesBufferingIoPipelineHandler,
    InboundQueueIoPipelineHandler,
):
    def __init__(
            self,
            *,
            filter: ta.Union[IoPipelineHandlerFn[ta.Any, bool], ta.Literal[True], None] = None,  # noqa
            passthrough: bool = False,
    ) -> None:
        if filter is True:
            filter = IoPipelineHandlerFns.no_context(ByteStreamBuffers.can_bytes)  # noqa

        super().__init__(
            filter=filter,  # noqa
            passthrough=passthrough,
        )

    _buffered_bytes: int = 0

    # @ta.override
    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        return self._buffered_bytes

    # @ta.override
    def _append(self, msg: ta.Any) -> None:
        bl = ByteStreamBuffers.bytes_len(msg, True)

        super()._append((msg, bl))

        if bl is not None:
            self._buffered_bytes += bl

    # @ta.override
    def _popleft(self) -> ta.Any:
        msg, bl = self._q.popleft()

        if bl is not None:
            self._buffered_bytes -= bl

        return msg


########################################
# ../handlers/flatmap.py


##


FlatMapIoPipelineHandlerFn = IoPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


class FlatMapIoPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class Filter:
        pred: IoPipelineHandlerFn[ta.Any, bool]
        fn: FlatMapIoPipelineHandlerFn
        else_fn: ta.Optional[FlatMapIoPipelineHandlerFn] = None

        def __repr__(self) -> str:
            return (
                f'{type(self).__name__}('
                f'{self.pred!r}'
                f', {self.fn!r}'
                f'{f", else_fn={self.else_fn!r}" if self.else_fn is not None else ""}'
                f')'
            )

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.pred(ctx, msg):
                yield from self.fn(ctx, msg)
            elif (ef := self.else_fn) is not None:
                yield from ef(ctx, msg)  # noqa
            else:
                yield msg

    @classmethod
    def filter(
            cls,
            pred: IoPipelineHandlerFn[ta.Any, bool],
            fn: FlatMapIoPipelineHandlerFn,
            else_fn: ta.Optional[FlatMapIoPipelineHandlerFn] = None,
    ) -> FlatMapIoPipelineHandlerFn:
        return cls.Filter(pred, fn, else_fn)

    @classmethod
    def filter_type(
            cls,
            ty: ta.Union[type, ta.Tuple[type, ...]],
            fn: FlatMapIoPipelineHandlerFn,
            else_fn: ta.Optional[FlatMapIoPipelineHandlerFn] = None,
    ) -> FlatMapIoPipelineHandlerFn:
        return cls.filter(IoPipelineHandlerFns.isinstance(ty), fn, else_fn)

    #

    @dc.dataclass(frozen=True)
    class Concat:
        fns: ta.Sequence[FlatMapIoPipelineHandlerFn]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            for fn in self.fns:
                yield from fn(ctx, msg)

    @classmethod
    def concat(cls, *fns: FlatMapIoPipelineHandlerFn) -> FlatMapIoPipelineHandlerFn:
        return cls.Concat(fns)

    #

    @dc.dataclass(frozen=True)
    class Compose:
        fns: ta.Sequence[FlatMapIoPipelineHandlerFn]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        _fn: FlatMapIoPipelineHandlerFn = dc.field(init=False)

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

            def compose(cur, nxt, ctx, msg):
                for x in cur(ctx, msg):
                    yield from nxt(ctx, x)

            xf: ta.Any = lambda ctx, msg: (msg,)  # noqa
            for cf in reversed(self.fns):
                xf = functools.partial(compose, cf, xf)

            object.__setattr__(self, '_fn', xf)

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return self._fn(ctx, msg)

    @classmethod
    def compose(cls, *fns: FlatMapIoPipelineHandlerFn) -> FlatMapIoPipelineHandlerFn:
        return cls.Compose(fns)

    #

    @dc.dataclass(frozen=True)
    class Map:
        fn: IoPipelineHandlerFn[ta.Any, ta.Any]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return (self.fn(ctx, msg),)

    @classmethod
    def map(cls, fn: IoPipelineHandlerFn[ta.Any, ta.Any]) -> FlatMapIoPipelineHandlerFn:
        return cls.Map(fn)

    #

    @dc.dataclass(frozen=True)
    class Apply:
        fn: IoPipelineHandlerFn[ta.Any, None]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            self.fn(ctx, msg)
            return (msg,)

    @classmethod
    def apply(cls, fn: IoPipelineHandlerFn[ta.Any, None]) -> FlatMapIoPipelineHandlerFn:
        return cls.Apply(fn)

    #

    @dc.dataclass(frozen=True)
    class Feed:
        direction: IoPipelineDirectionOrDuplex

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.direction!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.direction == 'inbound':
                ctx.feed_in(msg)
            elif self.direction == 'outbound':
                ctx.feed_out(msg)
            else:
                raise RuntimeError(f'Unknown direction: {self.direction!r}')
            return (msg,)

    @classmethod
    def feed_in(cls) -> FlatMapIoPipelineHandlerFn:
        return cls.Feed('inbound')

    @classmethod
    def feed_out(cls) -> FlatMapIoPipelineHandlerFn:
        return cls.Feed('outbound')

    #

    @dc.dataclass(frozen=True)
    class Inject:
        before: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None
        after: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None

        def __repr__(self) -> str:
            return ''.join([
                f'{type(self).__name__}(',
                *', '.join([
                    *([f'before={self.before!r}'] if self.before is not None else []),
                    *([f'after={self.after!r}'] if self.after is not None else []),
                ]),
                ')',
            ])

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            out: ta.List[ta.Any] = []
            if (before := self.before) is not None:
                out.extend(before() if callable(before) else before)  # noqa
            out.append(msg)
            if (after := self.after) is not None:
                out.extend(after() if callable(after) else after)  # noqa
            return out

    @classmethod
    def inject(
            cls,
            *,
            before: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None,
            after: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None,
    ) -> FlatMapIoPipelineHandlerFn:
        return cls.Inject(
            before=before,
            after=after,
        )

    #

    @dc.dataclass(frozen=True)
    class Drop:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return ()

    @classmethod
    def drop(cls) -> FlatMapIoPipelineHandlerFn:
        return cls.Drop()

    #

    @dc.dataclass(frozen=True)
    class Nop:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return (msg,)

    @classmethod
    def nop(cls) -> FlatMapIoPipelineHandlerFn:
        return cls.Nop()


#


class FlatMapIoPipelineHandler(IoPipelineHandler, Abstract):
    def __init__(
            self,
            fn: FlatMapIoPipelineHandlerFn,
    ) -> None:
        super().__init__()

        self._fn = check.callable(fn)

    _fn: FlatMapIoPipelineHandlerFn

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._fn!r})'


#


class InboundFlatMapIoPipelineHandler(FlatMapIoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_in(x)


class OutboundFlatMapIoPipelineHandler(FlatMapIoPipelineHandler):
    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_out(x)


class DuplexFlatMapIoPipelineHandler(
    InboundFlatMapIoPipelineHandler,
    OutboundFlatMapIoPipelineHandler,
):
    pass


#


class FlatMapIoPipelineHandlers(NamespaceClass):
    _CLS_BY_DIRECTION: ta.ClassVar[ta.Mapping[IoPipelineDirectionOrDuplex, ta.Type[FlatMapIoPipelineHandler]]] = {  # noqa
        'inbound': InboundFlatMapIoPipelineHandler,
        'outbound': OutboundFlatMapIoPipelineHandler,
        'duplex': DuplexFlatMapIoPipelineHandler,
    }

    @classmethod
    def new(
            cls,
            direction: IoPipelineDirectionOrDuplex,
            fn: FlatMapIoPipelineHandlerFn,
    ) -> IoPipelineHandler:
        h_cls = cls._CLS_BY_DIRECTION[direction]
        return h_cls(fn)

    #

    _NOT_MUST_PROPAGATE: ta.ClassVar[IoPipelineHandlerFn[ta.Any, bool]] = IoPipelineHandlerFns.not_(
        IoPipelineHandlerFns.isinstance(IoPipelineMessages.MustPropagate),
    )

    @classmethod
    def _add_drop_filters(
            cls,
            fn: FlatMapIoPipelineHandlerFn,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> FlatMapIoPipelineHandlerFn:
        if filter is not None:
            fn = FlatMapIoPipelineHandlerFns.filter(filter, fn)

        if filter_type is not None:
            fn = FlatMapIoPipelineHandlerFns.filter_type(filter_type, fn)

        fn = FlatMapIoPipelineHandlerFns.filter(cls._NOT_MUST_PROPAGATE, fn)

        return fn

    @classmethod
    def drop(
            cls,
            direction: IoPipelineDirectionOrDuplex,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> IoPipelineHandler:
        return cls.new(
            direction,
            cls._add_drop_filters(
                FlatMapIoPipelineHandlerFns.drop(),
                filter=filter,
                filter_type=filter_type,
            ),
        )

    @classmethod
    def feed_out_and_drop(
            cls,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> IoPipelineHandler:
        return cls.new(
            'inbound',
            cls._add_drop_filters(
                FlatMapIoPipelineHandlerFns.compose(
                    FlatMapIoPipelineHandlerFns.feed_out(),
                    FlatMapIoPipelineHandlerFns.drop(),
                ),
                filter=filter,
                filter_type=filter_type,
            ),
        )


########################################
# ../../streams/direct.py


##


class BaseDirectByteStreamBufferLike(BaseByteStreamBufferLike, Abstract):
    def __init__(self, data: BytesLike) -> None:
        super().__init__()

        self._data = data
        if isinstance(data, memoryview):
            self._mv_ = data
        else:
            self._b_ = data

    _mv_: memoryview
    _b_: ta.Union[bytes, bytearray]

    def _mv(self) -> memoryview:
        try:
            return self._mv_
        except AttributeError:
            pass

        self._mv_ = mv = memoryview(self._b_)
        return mv

    def _b(self) -> ta.Union[bytes, bytearray]:
        try:
            return self._b_
        except AttributeError:
            pass

        self._b_ = b = ByteStreamBuffers.memoryview_to_bytes(self._mv_)  # noqa
        return b


class DirectByteStreamBufferView(BaseDirectByteStreamBufferLike, ByteStreamBufferView):
    def __len__(self) -> int:
        return len(self._data)

    def peek(self) -> memoryview:
        return self._mv()

    def segments(self) -> ta.Sequence[memoryview]:
        return (self._mv(),) if len(self._data) else ()

    def tobytes(self) -> bytes:
        if type(b := self._b()) is bytes:
            return b
        return bytes(b)


class DirectByteStreamBuffer(BaseDirectByteStreamBufferLike, ByteStreamBuffer):
    """
    A read-only ByteStreamBuffer that wraps existing bytes without copying.

    This is a lightweight, zero-copy wrapper around bytes/bytearray/memoryview that provides the full
    ByteStreamBuffer interface (find, rfind, split_to, advance, coalesce) without mutation capabilities.

    Strengths:
      - Zero-copy construction from existing data
      - Always contiguous (coalesce is trivial)
      - Fast find/rfind delegating to optimized bytes methods
      - Simple implementation with minimal overhead

    Use cases:
      - Parsing fixed/immutable data (HTTP requests, protocol messages)
      - Using framers/codecs on data already in memory
      - Avoiding buffer allocation/copying overhead when mutation isn't needed

    Important notes:
      - If constructed from a bytearray, the underlying data could still be mutated externally. This is by design -
        we're wrapping directly, not defensively copying.
      - This is a read-only buffer - it does not implement MutableByteStreamBuffer (no write/reserve/commit).
      - All views returned from split_to() remain valid as they reference the original underlying data.

    Example:
        >>> data = b'GET /path HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n'
        >>> buf = DirectByteStreamBuffer(data)
        >>> pos = buf.find(b'\\r\\n\\r\\n')
        >>> headers = buf.split_to(pos)
        >>> print(headers.tobytes())
        b'GET /path HTTP/1.1\\r\\nHost: example.com'
    """

    def __init__(self, data: BytesLike) -> None:
        super().__init__(data)

        self._rpos = 0

    def __len__(self) -> int:
        return len(self._data) - self._rpos

    def peek(self) -> memoryview:
        mv = self._mv()
        if self._rpos >= len(mv):
            return memoryview(b'')
        return mv[self._rpos:]

    def segments(self) -> ta.Sequence[memoryview]:
        mv = self.peek()
        return (mv,) if len(mv) else ()

    def advance(self, n: int, /) -> None:
        if n < 0 or n > len(self):
            raise ValueError(n)
        self._rpos += n

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW

        if not self._rpos and n == len(self._data):
            self._rpos += n
            return DirectByteStreamBufferView(self._data)

        mv = self._mv()
        view = mv[self._rpos:self._rpos + n]
        self._rpos += n
        return DirectByteStreamBufferView(view)

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        if not sub:
            return start

        b = self._b()
        idx = b.find(sub, self._rpos + start, self._rpos + end)
        return (idx - self._rpos) if idx >= 0 else -1

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        if not sub:
            return end

        b = self._b()
        idx = b.rfind(sub, self._rpos + start, self._rpos + end)
        return (idx - self._rpos) if idx >= 0 else -1

    def coalesce(self, n: int, /) -> memoryview:
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return memoryview(b'')

        # Always contiguous - just return the requested slice
        mv = self._mv()
        return mv[self._rpos:self._rpos + n]


##


_EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW = DirectByteStreamBufferView(b'')


def empty_byte_stream_buffer_view() -> ByteStreamBufferView:
    return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW


########################################
# ../../streams/scanning.py


##


class ScanningByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A MutableByteStreamBuffer wrapper that caches negative-find progress to avoid repeated rescans in trickle scenarios.

    It is intentionally conservative:
      - It only caches progress for the default find range (start==0, end is None).
      - It only caches *negative* results (i.e., "-1"): once a match is found, caching is not updated, to preserve the
        property that repeated `find(sub)` on an unchanged buffer yields the same answer.

    This is designed to help framing-style code that repeatedly does:
      - buf.write(...small...)
      - buf.find(delim)
      - (not found) repeat

    Pairs well with `LongestMatchDelimiterByteStreamFrameDecoder`.
    """

    def __init__(self, buf) -> None:
        super().__init__()

        self._buf = buf
        self._scan_from_by_sub: dict[bytes, int] = {}

    @property
    def max_size(self) -> ta.Optional[int]:
        return self._buf.max_size

    #

    def __len__(self) -> int:
        return len(self._buf)

    def peek(self) -> memoryview:
        return self._buf.peek()

    def segments(self) -> ta.Sequence[memoryview]:
        return self._buf.segments()

    #

    def advance(self, n: int, /) -> None:
        self._buf.advance(n)
        self._adjust_for_consume(n)

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        v = self._buf.split_to(n)
        self._adjust_for_consume(n)
        return v

    def coalesce(self, n: int, /) -> memoryview:
        return self._buf.coalesce(n)

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        if start != 0 or end is not None:
            return self._buf.find(sub, start, end)

        sub_len = len(sub)
        if sub_len <= 0:
            return self._buf.find(sub, start, end)

        scan_from = self._scan_from_by_sub.get(sub, 0)

        # Allow overlap so a match spanning old/new boundary is discoverable.
        overlap = sub_len - 1
        eff_start = scan_from - overlap
        if eff_start < 0:
            eff_start = 0

        i = self._buf.find(sub, eff_start, None)
        if i < 0:
            self._scan_from_by_sub[sub] = len(self._buf)

        return i

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        # rfind isn't the typical trickle hot-path; delegate.
        return self._buf.rfind(sub, start, end)

    #

    def write(self, data: BytesLike, /) -> None:
        self._buf.write(data)

    def reserve(self, n: int, /) -> memoryview:
        return self._buf.reserve(n)

    def commit(self, n: int, /) -> None:
        self._buf.commit(n)

    #

    def _adjust_for_consume(self, n: int) -> None:
        if not self._scan_from_by_sub:
            return

        if n <= 0:
            return

        # Only front-consumption exists in this buffer model.
        for k, v in list(self._scan_from_by_sub.items()):
            nv = v - n
            if nv <= 0:
                self._scan_from_by_sub.pop(k, None)
            else:
                self._scan_from_by_sub[k] = nv


########################################
# ../../../logs/base.py


##


class AnyLogger(AnyLoggerMetricCollector[T], Abstract, ta.Generic[T]):
    def is_enabled_for(self, level: LogLevel) -> bool:
        return level >= self.get_effective_level()

    @abc.abstractmethod
    def get_effective_level(self) -> LogLevel:
        raise NotImplementedError

    #

    @ta.final
    def isEnabledFor(self, level: LogLevel) -> bool:  # noqa
        return self.is_enabled_for(level)

    @ta.final
    def getEffectiveLevel(self) -> LogLevel:  # noqa
        return self.get_effective_level()

    ##

    # This will be 1 for [Sync]Logger and 0 for AsyncLogger - in sync loggers these methods remain present on the stack,
    # in async loggers they return a coroutine to be awaited and thus aren't actually present when said coroutine is
    # awaited.
    _level_proxy_method_stack_offset: int

    @ta.overload
    def log(self, level: LogLevel, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def log(self, level: LogLevel, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def log(self, level: LogLevel, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def log(self, level: LogLevel, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                level,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def debug(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def debug(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def debug(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.DEBUG,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def info(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def info(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def info(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.INFO,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def warning(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def warning(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def warning(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.WARNING,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def error(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def error(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def error(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.ERROR,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def exception(self, exc: BaseException, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg: str, *args: ta.Any, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg: ta.Tuple[ta.Any, ...], *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg_fn: LoggingMsgFn, *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def exception(self, *args, exc_info=True, **kwargs):
        if not args:
            if not exc_info:
                raise TypeError('exc_info=False is not allowed when no args are passed')
            args = ((),)
        elif len(args) == 1:
            if isinstance(arg0 := args[0], BaseException):
                if exc_info is not True:  # noqa
                    raise TypeError(f'exc_info={exc_info!r} is not allowed when exc={arg0!r} is passed')
            args, exc_info = ((),), arg0

        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.ERROR,
                exc_info=exc_info,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def critical(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def critical(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def critical(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.CRITICAL,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @abc.abstractmethod
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> T:
        raise NotImplementedError


class Logger(LoggerMetricCollector, AnyLogger[None], Abstract):
    _level_proxy_method_stack_offset: int = 1

    @abc.abstractmethod
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> None:
        raise NotImplementedError


class AsyncLogger(AsyncLoggerMetricCollector, AnyLogger[ta.Awaitable[None]], Abstract):
    _level_proxy_method_stack_offset: int = 0

    @abc.abstractmethod
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> ta.Awaitable[None]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AnyNopLogger(AnyNopLoggerMetricCollector[T], AnyLogger[T], Abstract):
    @ta.final
    def get_effective_level(self) -> LogLevel:
        return -999


class NopLogger(NopLoggerMetricCollector, AnyNopLogger[None], Logger):
    @ta.final
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        pass


class AsyncNopLogger(AsyncNopLoggerMetricCollector, AnyNopLogger[ta.Awaitable[None]], AsyncLogger):
    @ta.final
    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        pass


########################################
# ../../../logs/std/records.py
"""
TODO:
 - TypedDict?
"""


##


class LoggingContextInfoRecordAdapters:
    # Ref:
    #  - https://docs.python.org/3/library/logging.html#logrecord-attributes
    #
    # LogRecord:
    #  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L276 (3.8)  # noqa
    #  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L286 (~3.14)  # noqa
    #

    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    class Adapter(Abstract, ta.Generic[T]):
        @property
        @abc.abstractmethod
        def info_cls(self) -> ta.Type[LoggingContextInfo]:
            raise NotImplementedError

        #

        @ta.final
        class NOT_SET:  # noqa
            def __new__(cls, *args, **kwargs):  # noqa
                raise TypeError

        class RecordAttr(ta.NamedTuple):
            name: str
            type: ta.Any
            default: ta.Any

        # @abc.abstractmethod
        record_attrs: ta.ClassVar[ta.Mapping[str, RecordAttr]]

        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Union[
            ta.Mapping[str, ta.Any],
            ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]],
        ]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[T]:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            if Abstract in cls.__bases__:
                return

            if 'record_attrs' in cls.__dict__:
                raise TypeError(cls)
            if not isinstance(ra := cls.__dict__['_record_attrs'], collections.abc.Mapping):
                raise TypeError(ra)

            rd: ta.Dict[str, LoggingContextInfoRecordAdapters.Adapter.RecordAttr] = {}
            for n, v in ra.items():
                if not n or not isinstance(n, str) or n in rd:
                    raise AttributeError(n)
                if isinstance(v, tuple):
                    t, d = v
                else:
                    t, d = v, cls.NOT_SET
                rd[n] = cls.RecordAttr(
                    name=n,
                    type=t,
                    default=d,
                )
            cls.record_attrs = rd

    class RequiredAdapter(Adapter[T], Abstract):
        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @ta.final
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(self.info_cls)) is not None:
                return self._info_to_record(info)
            else:
                raise TypeError  # FIXME: fallback?

        @abc.abstractmethod
        def _info_to_record(self, info: T) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def record_to_info(self, rec: logging.LogRecord) -> T:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            if any(a.default is not cls.NOT_SET for a in cls.record_attrs.values()):
                raise TypeError(cls.record_attrs)

    class OptionalAdapter(Adapter[T], Abstract, ta.Generic[T]):
        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]:
            raise NotImplementedError

        record_defaults: ta.ClassVar[ta.Mapping[str, ta.Any]]

        #

        @ta.final
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(self.info_cls)) is not None:
                return self._info_to_record(info)
            else:
                return self.record_defaults

        @abc.abstractmethod
        def _info_to_record(self, info: T) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            dd: ta.Dict[str, ta.Any] = {a.name: a.default for a in cls.record_attrs.values()}
            if any(d is cls.NOT_SET for d in dd.values()):
                raise TypeError(cls.record_attrs)
            cls.record_defaults = dd

    #

    class Name(RequiredAdapter[LoggingContextInfos.Name]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Name]] = LoggingContextInfos.Name

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Name of the logger used to log the call. Unmodified by ctor.
            name=str,
        )

        def _info_to_record(self, info: LoggingContextInfos.Name) -> ta.Mapping[str, ta.Any]:
            return dict(
                name=info.name,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Name:
            return LoggingContextInfos.Name(
                name=rec.name,
            )

    class Level(RequiredAdapter[LoggingContextInfos.Level]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Level]] = LoggingContextInfos.Level

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Set to
            # `getLevelName(level)`.
            levelname=str,

            # Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL). Unmodified by ctor.
            levelno=int,
        )

        def _info_to_record(self, info: LoggingContextInfos.Level) -> ta.Mapping[str, ta.Any]:
            return dict(
                levelname=info.name,
                levelno=int(info.level),
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Level:
            return LoggingContextInfos.Level.build(rec.levelno)

    class Msg(RequiredAdapter[LoggingContextInfos.Msg]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Msg]] = LoggingContextInfos.Msg

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # The format string passed in the original logging call. Merged with args to produce message, or an
            # arbitrary object (see Using arbitrary objects as messages). Unmodified by ctor.
            msg=str,

            # The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge
            # (when there is only one argument, and it is a dictionary). Ctor will transform a 1-tuple containing a
            # Mapping into just the mapping, but is otherwise unmodified.
            args=ta.Union[tuple, dict, None],
        )

        def _info_to_record(self, info: LoggingContextInfos.Msg) -> ta.Mapping[str, ta.Any]:
            return dict(
                msg=info.msg,
                args=info.args,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Msg:
            return LoggingContextInfos.Msg(
                msg=rec.msg,
                args=rec.args,
            )

    class Time(RequiredAdapter[LoggingContextInfos.Time]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Time]] = LoggingContextInfos.Time

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Time when the LogRecord was created. Set to `time.time_ns() / 1e9` for >=3.13.0b1, otherwise simply
            # `time.time()`.
            #
            # See:
            #  - https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            #  - https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
            #
            created=float,

            # Millisecond portion of the time when the LogRecord was created.
            msecs=float,

            # Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
            relativeCreated=float,
        )

        def _info_to_record(self, info: LoggingContextInfos.Time) -> ta.Mapping[str, ta.Any]:
            return dict(
                created=info.secs,
                msecs=info.msecs,
                relativeCreated=info.relative_secs,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Time:
            return LoggingContextInfos.Time.build(
                int(rec.created * 1e9),
            )

    class Exc(OptionalAdapter[LoggingContextInfos.Exc]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Exc]] = LoggingContextInfos.Exc

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Exception tuple (à la sys.exc_info) or, if no exception has occurred, None. Unmodified by ctor.
            exc_info=(ta.Optional[LoggingExcInfoTuple], None),

            # Used to cache the traceback text. Simply set to None by ctor, later set by Formatter.format.
            exc_text=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Exc) -> ta.Mapping[str, ta.Any]:
            return dict(
                exc_info=info.info_tuple,
                exc_text=None,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Exc]:
            # FIXME:
            # error: Argument 1 to "build" of "Exc" has incompatible type
            # "tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None"; expected  # noqa
            # "BaseException | tuple[type[BaseException], BaseException, TracebackType | None] | bool | None"  [arg-type]  # noqa
            return LoggingContextInfos.Exc.build(rec.exc_info)  # type: ignore[arg-type]

    class Caller(OptionalAdapter[LoggingContextInfos.Caller]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Caller]] = LoggingContextInfos.Caller

        _UNKNOWN_PATH_NAME: ta.ClassVar[str] = '(unknown file)'
        _UNKNOWN_FUNC_NAME: ta.ClassVar[str] = '(unknown function)'

        _STACK_INFO_PREFIX: ta.ClassVar[str] = 'Stack (most recent call last):\n'

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Full pathname of the source file where the logging call was issued (if available). Unmodified by ctor. May
            # default to "(unknown file)" by Logger.findCaller / Logger._log.
            pathname=(str, _UNKNOWN_PATH_NAME),

            # Source line number where the logging call was issued (if available). Unmodified by ctor. May default to 0
            # by Logger.findCaller / Logger._log.
            lineno=(int, 0),

            # Name of function containing the logging call. Set by ctor to `func` arg, unmodified. May default to
            # "(unknown function)" by Logger.findCaller / Logger._log.
            funcName=(str, _UNKNOWN_FUNC_NAME),

            # Stack frame information (where available) from the bottom of the stack in the current thread, up to and
            # including the stack frame of the logging call which resulted in the creation of this record. Set by ctor
            # to `sinfo` arg, unmodified. Mostly set, if requested, by `Logger.findCaller`, to
            # `traceback.print_stack(f)`, but prepended with the literal "Stack (most recent call last):\n", and
            # stripped of exactly one trailing `\n` if present.
            stack_info=(ta.Optional[str], None),
        )

        def _info_to_record(self, caller: LoggingContextInfos.Caller) -> ta.Mapping[str, ta.Any]:
            if (sinfo := caller.stack_info) is not None:
                stack_info: ta.Optional[str] = '\n'.join([
                    self._STACK_INFO_PREFIX,
                    sinfo[1:] if sinfo.endswith('\n') else sinfo,
                ])
            else:
                stack_info = None

            return dict(
                pathname=caller.file_path,

                lineno=caller.line_no,
                funcName=caller.func_name,

                stack_info=stack_info,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Caller]:
            # FIXME: piecemeal?
            if (
                    rec.pathname != self._UNKNOWN_PATH_NAME and
                    rec.lineno != 0 and
                    rec.funcName != self._UNKNOWN_FUNC_NAME
            ):
                if (sinfo := rec.stack_info) is not None and sinfo.startswith(self._STACK_INFO_PREFIX):
                    sinfo = sinfo[len(self._STACK_INFO_PREFIX):]
                return LoggingContextInfos.Caller(
                    file_path=rec.pathname,

                    line_no=rec.lineno,
                    func_name=rec.funcName,

                    stack_info=sinfo,
                )

            return None

    class SourceFile(Adapter[LoggingContextInfos.SourceFile]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.SourceFile]] = LoggingContextInfos.SourceFile

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Filename portion of pathname. Set to `os.path.basename(pathname)` if successful, otherwise defaults to
            # pathname.
            filename=str,

            # Module (name portion of filename). Set to `os.path.splitext(filename)[0]`, otherwise defaults to
            # "Unknown module".
            module=str,
        )

        _UNKNOWN_MODULE: ta.ClassVar[str] = 'Unknown module'

        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(LoggingContextInfos.SourceFile)) is not None:
                return dict(
                    filename=info.file_name,
                    module=info.module,
                )

            if (caller := ctx.get_info(LoggingContextInfos.Caller)) is not None:
                return dict(
                    filename=caller.file_path,
                    module=self._UNKNOWN_MODULE,
                )

            return dict(
                filename=LoggingContextInfoRecordAdapters.Caller._UNKNOWN_PATH_NAME,  # noqa
                module=self._UNKNOWN_MODULE,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.SourceFile]:
            if (
                    rec.module is not None and
                    rec.module != self._UNKNOWN_MODULE
            ):
                return LoggingContextInfos.SourceFile(
                    file_name=rec.filename,
                    module=rec.module,  # FIXME: piecemeal?
                )

            return None

    class Thread(OptionalAdapter[LoggingContextInfos.Thread]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Thread]] = LoggingContextInfos.Thread

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Thread ID if available, and `logging.logThreads` is truthy.
            thread=(ta.Optional[int], None),

            # Thread name if available, and `logging.logThreads` is truthy.
            threadName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Thread) -> ta.Mapping[str, ta.Any]:
            if logging.logThreads:
                return dict(
                    thread=info.ident,
                    threadName=info.name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Thread]:
            if (
                    (ident := rec.thread) is not None and
                    (name := rec.threadName) is not None
            ):
                return LoggingContextInfos.Thread(
                    ident=ident,
                    native_id=None,
                    name=name,
                )

            return None

    class Process(OptionalAdapter[LoggingContextInfos.Process]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Process]] = LoggingContextInfos.Process

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Process ID if available - that is, if `hasattr(os, 'getpid')` - and `logging.logProcesses` is truthy,
            # otherwise None.
            process=(ta.Optional[int], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Process) -> ta.Mapping[str, ta.Any]:
            if logging.logProcesses:
                return dict(
                    process=info.pid,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Process]:
            if (
                    (pid := rec.process) is not None
            ):
                return LoggingContextInfos.Process(
                    pid=pid,
                )

            return None

    class Multiprocessing(OptionalAdapter[LoggingContextInfos.Multiprocessing]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Multiprocessing]] = LoggingContextInfos.Multiprocessing

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Process name if available. Set to None if `logging.logMultiprocessing` is not truthy. Otherwise, set to
            # 'MainProcess', then `sys.modules.get('multiprocessing').current_process().name` if that works, otherwise
            # remains as 'MainProcess'.
            #
            # As noted by stdlib:
            #
            #   Errors may occur if multiprocessing has not finished loading yet - e.g. if a custom import hook causes
            #   third-party code to run when multiprocessing calls import. See issue 8200 for an example
            #
            processName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Multiprocessing) -> ta.Mapping[str, ta.Any]:
            if logging.logMultiprocessing:
                return dict(
                    processName=info.process_name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Multiprocessing]:
            if (
                    (process_name := rec.processName) is not None
            ):
                return LoggingContextInfos.Multiprocessing(
                    process_name=process_name,
                )

            return None

    class AsyncioTask(OptionalAdapter[LoggingContextInfos.AsyncioTask]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.AsyncioTask]] = LoggingContextInfos.AsyncioTask

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Union[ta.Any, ta.Tuple[ta.Any, ta.Any]]]] = dict(
            # Absent <3.12, otherwise asyncio.Task name if available, and `logging.logAsyncioTasks` is truthy. Set to
            # `sys.modules.get('asyncio').current_task().get_name()`, otherwise None.
            taskName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.AsyncioTask) -> ta.Mapping[str, ta.Any]:
            if getattr(logging, 'logAsyncioTasks', None):  # Absent <3.12
                return dict(
                    taskName=info.name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.AsyncioTask]:
            if (
                    (name := getattr(rec, 'taskName', None)) is not None
            ):
                return LoggingContextInfos.AsyncioTask(
                    name=name,
                )

            return None


_LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_: ta.Sequence[LoggingContextInfoRecordAdapters.Adapter] = [  # noqa
    LoggingContextInfoRecordAdapters.Name(),
    LoggingContextInfoRecordAdapters.Level(),
    LoggingContextInfoRecordAdapters.Msg(),
    LoggingContextInfoRecordAdapters.Time(),
    LoggingContextInfoRecordAdapters.Exc(),
    LoggingContextInfoRecordAdapters.Caller(),
    LoggingContextInfoRecordAdapters.SourceFile(),
    LoggingContextInfoRecordAdapters.Thread(),
    LoggingContextInfoRecordAdapters.Process(),
    LoggingContextInfoRecordAdapters.Multiprocessing(),
    LoggingContextInfoRecordAdapters.AsyncioTask(),
]

_LOGGING_CONTEXT_INFO_RECORD_ADAPTERS: ta.Mapping[ta.Type[LoggingContextInfo], LoggingContextInfoRecordAdapters.Adapter] = {  # noqa
    ad.info_cls: ad for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_
}


##


# Formatter:
#  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L514 (3.8)
#  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L554 (~3.14)  # noqa
#
_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS: ta.Dict[str, ta.Any] = dict(
    # The logged message, computed as msg % args. Set to `record.getMessage()`.
    message=str,

    # Human-readable time when the LogRecord was created. By default this is of the form '2003-07-08 16:49:45,896' (the
    # numbers after the comma are millisecond portion of the time). Set to `self.formatTime(record, self.datefmt)` if
    # `self.usesTime()`, otherwise unset.
    asctime=str,

    # Used to cache the traceback text. If unset (falsey) on the record and `exc_info` is truthy, set to
    # `self.formatException(record.exc_info)` - otherwise unmodified.
    exc_text=ta.Optional[str],
)


##


_KNOWN_STD_LOGGING_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(
    a for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS.values() for a in ad.record_attrs
)

_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS)


class UnknownStdLoggingRecordAttrsWarning(LoggingSetupWarning):
    pass


def _check_std_logging_record_attrs() -> None:
    if (
            len([a for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS.values() for a in ad.record_attrs]) !=
            len(_KNOWN_STD_LOGGING_RECORD_ATTR_SET)
    ):
        raise RuntimeError('Duplicate LoggingContextInfoRecordAdapter record attrs')

    rec_dct = dict(logging.makeLogRecord({}).__dict__)

    if (unk_rec_fields := frozenset(rec_dct) - _KNOWN_STD_LOGGING_RECORD_ATTR_SET):
        import warnings  # noqa

        warnings.warn(
            f'Unknown log record attrs detected: {sorted(unk_rec_fields)!r}',
            UnknownStdLoggingRecordAttrsWarning,
        )


_check_std_logging_record_attrs()


##


class LoggingContextLogRecord(logging.LogRecord):
    # LogRecord.__init__ args:
    #  - name: str
    #  - level: int
    #  - pathname: str - Confusingly referred to as `fn` before the LogRecord ctor. May be empty or "(unknown file)".
    #  - lineno: int - May be 0.
    #  - msg: str
    #  - args: tuple | dict | 1-tuple[dict]
    #  - exc_info: LoggingExcInfoTuple | None
    #  - func: str | None = None -> funcName
    #  - sinfo: str | None = None -> stack_info
    #

    def __init__(self, *, _logging_context: LoggingContext) -> None:  # noqa
        self.__dict__.update(_logging_context=_logging_context)

        for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_:
            self.__dict__.update(ad.context_to_record(_logging_context))

    _logging_context: LoggingContext

    # FIXME: track extra
    # def __setattr__(self, key, value):
    #     super().__setattr__(key, value)


##


@ta.final
class LogRecordLoggingContext(LoggingContext):
    def __init__(self, rec: logging.LogRecord) -> None:
        if isinstance(rec, LoggingContextLogRecord):
            raise TypeError(rec)

        self._rec = rec

        infos: ta.List[LoggingContextInfo] = [
            info
            for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_
            if (info := ad.record_to_info(rec)) is not None
        ]

        # FIXME:
        # if extra is not None:
        #     for key in extra:
        #         if (key in ["message", "asctime"]) or (key in rv.__dict__):
        #             raise KeyError("Attempt to overwrite %r in LogRecord" % key)
        #         rv.__dict__[key] = extra[key]

        if (extra := {
            a: v
            for a, v in rec.__dict__.items()
            if a not in _KNOWN_STD_LOGGING_RECORD_ATTR_SET
        }):
            infos.append(LoggingContextInfos.Extra(extra))

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {
            type(info): info
            for info in infos
        }

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)


########################################
# ../../streams/segmented.py


##


class SegmentedByteStreamBufferView(BaseByteStreamBufferLike, ByteStreamBufferView):
    """
    A read-only, possibly non-contiguous view over a sequence of byte segments.

    This is intended to be produced by `SegmentedByteStreamBuffer.split_to()` without copying.
    """

    def __init__(self, segs: ta.Sequence[memoryview]) -> None:
        super().__init__()

        self._segs = tuple(segs)
        for mv in self._segs:
            if (mvl := len(mv)) < 1:
                raise ValueError('Empty segment')
            self._len += mvl

    @classmethod
    def of_opt(cls, segs: ta.Sequence[memoryview]) -> ta.Optional['SegmentedByteStreamBufferView']:
        if not segs:
            return None
        return cls(segs)

    @classmethod
    def or_else(cls, segs: ta.Sequence[memoryview], default: T) -> ta.Union['SegmentedByteStreamBufferView', T]:
        if not segs:
            return default
        return cls(segs)

    _len = 0

    def __len__(self) -> int:
        return self._len

    def peek(self) -> memoryview:
        if not self._segs:
            return memoryview(b'')
        return self._segs[0]

    def segments(self) -> ta.Sequence[memoryview]:
        return self._segs

    def tobytes(self) -> bytes:
        if not self._segs:
            return b''
        if len(self._segs) == 1:
            return ByteStreamBuffers.memoryview_to_bytes(self._segs[0])
        return b''.join(ByteStreamBuffers.memoryview_to_bytes(mv) for mv in self._segs)


class SegmentedByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A segmented, consumption-oriented bytes buffer.

    Internally stores a list of `bytes`/`bytearray` segments plus a head offset. Exposes readable data as `memoryview`
    segments without copying.

    Optional "chunked writes":
      - If chunk_size > 0, small writes are accumulated into a lazily-allocated active bytearray "chunk" up to
        chunk_size.
      - Writes >= chunk_size are stored as their own segments (after flushing any active chunk).
      - On flush, the active chunk is kept as a bytearray segment iff it is at least `chunk_compact_threshold` full;
        otherwise it is materialized as bytes to avoid pinning a large capacity for tiny content.

    Reserve/commit:
      - If chunk_size > 0 and reserve(n) fits in the active chunk, the reservation is carved from the active chunk.
        Reserved bytes are not readable until commit().
      - If reserve(n) does not fit, the active chunk is flushed first.
      - If n <= chunk_size after flushing, the reservation is served from a new active chunk (so the remainder becomes
        the next active chunk).
      - If n > chunk_size, reserve allocates a dedicated buffer and on commit it is "closed" (it does not become the
        next active chunk).

    Important exported-view caveat:
      - reserve() returns a memoryview. As long as any exported memoryview exists, the underlying bytearray must not be
        resized, or Python will raise BufferError. Therefore the active chunk bytearray is *fixed capacity*
        (len==chunk_size) and we track "used" bytes separately, writing via slice assignment rather than extend().
    """

    def __init__(
            self,
            *,
            max_size: ta.Optional[int] = None,
            chunk_size: int = 0,
            chunk_compact_threshold: float = .25,
    ) -> None:
        super().__init__()

        self._segs: ta.List[ta.Union[bytes, bytearray]] = []

        self._max_size = None if max_size is None else int(max_size)

        if chunk_size < 0:
            raise ValueError(chunk_size)
        self._chunk_size = chunk_size

        if not (0.0 <= chunk_compact_threshold <= 1.0):
            raise ValueError(chunk_compact_threshold)
        self._chunk_compact_threshold = chunk_compact_threshold

        self._active: ta.Optional[bytearray] = None
        self._active_used = 0

    @property
    def max_size(self) -> ta.Optional[int]:
        return self._max_size

    _head_off = 0
    _len = 0

    _reserved: ta.Optional[bytearray] = None
    _reserved_len = 0
    _reserved_in_active = False

    #

    def __len__(self) -> int:
        return self._len

    def _active_readable_len(self) -> int:
        if self._active is None:
            return 0
        if self._reserved_in_active and self._reserved is not None:
            tail = self._reserved_len
        else:
            tail = 0
        rl = self._active_used - tail
        return rl if rl > 0 else 0

    def peek(self) -> memoryview:
        if not self._segs:
            return memoryview(b'')

        s0 = self._segs[0]
        mv = memoryview(s0)
        if self._head_off:
            mv = mv[self._head_off:]

        if s0 is self._active:
            # Active is only meaningful by _active_used, not len(bytearray).
            rl = self._active_readable_len()
            if self._head_off >= rl:
                return memoryview(b'')
            mv = memoryview(self._active)[self._head_off:rl]
            return mv

        return mv

    def segments(self) -> ta.Sequence[memoryview]:
        if not self._segs:
            return ()

        out: ta.List[memoryview] = []

        last_i = len(self._segs) - 1
        for i, s in enumerate(self._segs):
            if s is self._active and i == last_i:
                # Active chunk: create fresh view with readable length.
                rl = self._active_readable_len()
                if not i:
                    # Active is also first segment; apply head_off.
                    if self._head_off >= rl:
                        continue
                    mv = memoryview(self._active)[self._head_off:rl]
                else:
                    if rl <= 0:
                        continue
                    mv = memoryview(self._active)[:rl]
            else:
                # Non-active segment.
                mv = memoryview(s)
                if not i and self._head_off:
                    mv = mv[self._head_off:]

            if len(mv):
                out.append(mv)

        return out

    #

    def _ensure_active(self) -> bytearray:
        if self._chunk_size <= 0:
            raise RuntimeError('no active chunk without chunk_size')

        a = self._active
        if a is None:
            a = bytearray(self._chunk_size)  # fixed capacity
            self._segs.append(a)
            self._active = a
            self._active_used = 0

        return a

    def _flush_active(self) -> None:
        if (a := self._active) is None:
            return

        if self._reserved_in_active:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        if (used := self._active_used) <= 0:
            if self._segs and self._segs[-1] is a:
                self._segs.pop()
            self._active = None
            self._active_used = 0
            return

        # If under threshold, always bytes() to avoid pinning.
        if self._chunk_size and (float(used) / float(self._chunk_size)) < self._chunk_compact_threshold:
            if not self._segs or self._segs[-1] is not a:
                raise RuntimeError('active not at tail')
            self._segs[-1] = ByteStreamBuffers.memoryview_to_bytes(memoryview(a)[:used])

        else:
            # Try to shrink in-place to used bytes. If exported views exist, this can BufferError; fall back to bytes()
            # in that case.
            if not self._segs or self._segs[-1] is not a:
                raise RuntimeError('active not at tail')
            try:
                del a[used:]  # may raise BufferError if any exports exist
            except BufferError:
                self._segs[-1] = ByteStreamBuffers.memoryview_to_bytes(memoryview(a)[:used])

        self._active = None
        self._active_used = 0

    def write(self, data: BytesLike, /) -> None:
        if not data:
            return
        if isinstance(data, memoryview):
            data = ByteStreamBuffers.memoryview_to_bytes(data)  # noqa
        # elif isinstance(data, bytearray):
        #     pass
        # else:
        #     pass

        dl = len(data)

        if self._max_size is not None and self._len + dl > self._max_size:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_size')

        if self._chunk_size <= 0:
            self._segs.append(data)
            self._len += dl
            return

        if self._reserved_in_active:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        if dl >= self._chunk_size:
            self._flush_active()
            self._segs.append(data)
            self._len += dl
            return

        a = self._ensure_active()
        if self._active_used + dl > self._chunk_size:
            self._flush_active()
            a = self._ensure_active()

        # Copy into fixed-capacity buffer; do not resize.
        memoryview(a)[self._active_used:self._active_used + dl] = data
        self._active_used += dl
        self._len += dl

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._reserved is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        if self._chunk_size <= 0:
            b = bytearray(n)
            self._reserved = b
            self._reserved_len = n
            self._reserved_in_active = False
            return memoryview(b)

        if n > self._chunk_size:
            self._flush_active()
            b = bytearray(n)
            self._reserved = b
            self._reserved_len = n
            self._reserved_in_active = False
            return memoryview(b)

        # Ensure reservation fits in active; otherwise flush then create a new one.
        if self._active is not None and (self._active_used + n > self._chunk_size):
            self._flush_active()

        a = self._ensure_active()

        start = self._active_used
        # Reservation does not change _active_used (not readable until commit).
        self._reserved = a
        self._reserved_len = n
        self._reserved_in_active = True
        return memoryview(a)[start:start + n]

    def commit(self, n: int, /) -> None:
        if self._reserved is None:
            raise NoOutstandingReserveByteStreamBufferError('no outstanding reserve')
        if n < 0 or n > self._reserved_len:
            raise ValueError(n)

        if self._reserved_in_active:
            a = self._reserved
            self._reserved = None
            self._reserved_len = 0
            self._reserved_in_active = False

            if self._max_size is not None and self._len + n > self._max_size:
                raise BufferTooLargeByteStreamBufferError('buffer exceeded max_size')

            if n:
                self._active_used += n
                self._len += n

            # Keep active for reuse.
            self._active = a
            return

        b = self._reserved
        self._reserved = None
        self._reserved_len = 0
        self._reserved_in_active = False

        if self._max_size is not None and self._len + n > self._max_size:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_size')

        if not n:
            return

        if n == len(b):
            self._segs.append(b)
            self._len += n
        else:
            bb = ByteStreamBuffers.memoryview_to_bytes(memoryview(b)[:n])
            self._segs.append(bb)
            self._len += n

    #

    def advance(self, n: int, /) -> None:
        if n < 0 or n > self._len:
            raise ValueError(n)
        if not n:
            return

        self._len -= n

        while n and self._segs:
            s0 = self._segs[0]

            if s0 is self._active:
                avail0 = self._active_readable_len() - self._head_off
            else:
                avail0 = len(s0) - self._head_off

            if avail0 <= 0:
                popped = self._segs.pop(0)
                if popped is self._active:
                    self._active = None
                    self._active_used = 0
                self._head_off = 0
                continue

            if n < avail0:
                self._head_off += n
                return

            n -= avail0
            popped = self._segs.pop(0)
            if popped is self._active:
                self._active = None
                self._active_used = 0
            self._head_off = 0

        if n:
            raise RuntimeError(n)

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        if n < 0 or n > self._len:
            raise ValueError(n)
        if not n:
            return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW

        out: ta.List[memoryview] = []
        rem = n

        while rem:
            if not self._segs:
                raise RuntimeError(rem)

            s0 = self._segs[0]

            if s0 is self._active:
                rl = self._active_readable_len()
                if self._head_off >= rl:
                    raise RuntimeError(rem)
                mv0 = memoryview(s0)[self._head_off:rl]
            else:
                mv0 = memoryview(s0)
                if self._head_off:
                    mv0 = mv0[self._head_off:]

            if rem < len(mv0):
                out.append(mv0[:rem])
                self._head_off += rem
                self._len -= n
                return byte_stream_buffer_view_from_segments(out)

            out.append(mv0)
            rem -= len(mv0)
            popped = self._segs.pop(0)
            if popped is self._active:
                self._active = None
                self._active_used = 0
            self._head_off = 0

        self._len -= n
        return byte_stream_buffer_view_from_segments(out)

    def coalesce(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if n > self._len:
            raise ValueError(n)
        if not n:
            return memoryview(b'')

        if self._reserved is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        mv0 = self.peek()
        if len(mv0) >= n:
            return mv0[:n]

        out = bytearray(n)
        w = 0

        new_segs: ta.List[ta.Union[bytes, bytearray]] = []

        seg_i = 0
        while w < n and seg_i < len(self._segs):
            s = self._segs[seg_i]
            off = self._head_off if not seg_i else 0

            seg_len = len(s) - off
            if s is self._active and seg_i == (len(self._segs) - 1):
                seg_len = self._active_readable_len() - off

            if seg_len <= 0:
                seg_i += 1
                continue

            take = n - w
            if take > seg_len:
                take = seg_len

            out[w:w + take] = memoryview(s)[off:off + take]
            w += take

            if take < seg_len:
                rem = s[off + take:off + seg_len]
                if rem:
                    new_segs.append(rem)
                seg_i += 1
                break

            seg_i += 1

        if seg_i < len(self._segs):
            new_segs.extend(self._segs[seg_i:])

        self._segs = [bytes(out), *new_segs]
        self._head_off = 0

        self._active = None
        self._active_used = 0

        return memoryview(self._segs[0])[:n]

    def _seg_readable_slice(
            self,
            si: int,
            s: ta.Union[bytes, bytearray],
            last_i: int,
    ) -> ta.Tuple[int, int]:
        """
        Compute the readable offset and length for segment at index si.

        Returns (offset, readable_len) where:
          - offset: byte offset into segment (head_off for si==0, else 0)
          - readable_len: number of readable bytes from offset (0 if segment empty/consumed)

        Handles head offset for first segment and active chunk readable length for last segment.
        """

        off = self._head_off if not si else 0
        seg_len = len(s) - off
        if s is self._active and si == last_i:
            seg_len = self._active_readable_len() - off
        return off, max(0, seg_len)

    def _seg_search_range(
            self,
            start: int,
            limit: int,
            m: int,
            seg_gs: int,
            seg_ge: int,
            seg_len: int,
    ) -> ta.Optional[ta.Tuple[int, int]]:
        """
        Compute local search range within a segment.

        Args:
            start: global start position (user-provided)
            limit: global limit (end - m, last valid position where match can start)
            m: pattern length
            seg_gs: segment global start position
            seg_ge: segment global end position
            seg_len: segment readable length

        Returns (local_start, local_end) if segment overlaps search range, else None.
          - local_start: offset within segment to start searching
          - local_end: offset within segment to end searching (exclusive)
        """

        # Check if segment overlaps search range
        if limit < seg_gs or start >= seg_ge:
            return None

        # Compute local start within segment
        ls = max(0, start - seg_gs)

        # Compute local end: can start match anywhere up to limit, need m bytes
        max_start_in_seg = limit - seg_gs
        end_search = min(max_start_in_seg + m, seg_len)

        # Validate range
        if ls >= end_search:
            return None

        return ls, end_search

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        m = len(sub)
        if m == 0:
            return start
        if end - start < m:
            return -1

        limit = end - m

        tail = b''
        tail_gstart = 0

        gpos = 0

        last_i = len(self._segs) - 1

        for si, s in enumerate(self._segs):
            off, seg_len = self._seg_readable_slice(si, s, last_i)
            if seg_len <= 0:
                continue

            seg_gs = gpos
            seg_ge = gpos + seg_len

            # Within-segment search
            search_range = self._seg_search_range(start, limit, m, seg_gs, seg_ge, seg_len)
            if search_range is not None:
                ls, end_search = search_range
                idx = s.find(sub, off + ls, off + end_search)
                if idx != -1:
                    return seg_gs + (idx - off)

            if m > 1 and tail:
                head_need = m - 1
                # Only read as many bytes as are actually available in this segment to avoid reading uninitialized data
                # from active chunks.
                head_avail = min(head_need, seg_len)
                if head_avail > 0:
                    head = s[off:off + head_avail]
                    comb = tail + head
                    j = comb.find(sub)
                    if j != -1 and j < len(tail) < j + m:
                        cand = tail_gstart + j
                        if start <= cand <= limit:
                            return cand

            if m > 1:
                take = m - 1
                if seg_len >= take:
                    tail = s[off + seg_len - take:off + seg_len]
                    tail_gstart = seg_ge - take
                else:
                    tail = (tail + s[off:off + seg_len])[-(m - 1):]
                    tail_gstart = seg_ge - len(tail)

            gpos = seg_ge

        return -1

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        m = len(sub)
        if m == 0:
            return end
        if end - start < m:
            return -1

        limit = end - m

        if not self._segs:
            return -1

        best = -1

        seg_ge = self._len
        prev_s: ta.Optional[ta.Union[bytes, bytearray]] = None
        prev_off = 0
        prev_seg_len = 0

        last_i = len(self._segs) - 1

        for si in range(len(self._segs) - 1, -1, -1):
            s = self._segs[si]
            off, seg_len = self._seg_readable_slice(si, s, last_i)
            if seg_len <= 0:
                continue

            seg_gs = seg_ge - seg_len

            # Within-segment search
            search_range = self._seg_search_range(start, limit, m, seg_gs, seg_ge, seg_len)
            if search_range is not None:
                ls, end_search = search_range
                idx = s.rfind(sub, off + ls, off + end_search)
                if idx != -1:
                    cand = seg_gs + (idx - off)
                    if cand > best:
                        best = cand

            if m > 1 and prev_s is not None:
                tail_need = m - 1
                if seg_len >= tail_need:
                    tail = s[off + seg_len - tail_need:off + seg_len]
                    tail_gstart = seg_ge - tail_need

                else:
                    tail_parts = [s[off:off + seg_len]]
                    tail_len = seg_len
                    for sj in range(si - 1, -1, -1):
                        if tail_len >= tail_need:
                            break

                        sj_s = self._segs[sj]
                        sj_off, sj_len = self._seg_readable_slice(sj, sj_s, last_i)
                        if sj_len <= 0:
                            continue

                        take = min(tail_need - tail_len, sj_len)
                        tail_parts.insert(0, sj_s[sj_off + sj_len - take:sj_off + sj_len])
                        tail_len += take

                    tail_combined = b''.join(tail_parts)
                    tail = tail_combined[-(m - 1):] if len(tail_combined) >= m - 1 else tail_combined
                    tail_gstart = seg_ge - len(tail)

                head_need = m - 1
                # Only read as many bytes as are actually available in prev segment to avoid reading uninitialized data
                # from active chunks.
                head_avail = min(head_need, prev_seg_len)
                if head_avail > 0:
                    head = prev_s[prev_off:prev_off + head_avail]
                else:
                    head = b''

                comb = tail + head
                j = comb.rfind(sub)
                if j != -1 and j < len(tail) < j + m:
                    cand = tail_gstart + j
                    if start <= cand <= limit and cand > best:
                        best = cand

            if best >= seg_gs:
                return best

            prev_s = s
            prev_off = off
            prev_seg_len = seg_len
            seg_ge = seg_gs

        return best


##


def byte_stream_buffer_view_from_segments(mvs: ta.Sequence[memoryview]) -> ByteStreamBufferView:
    if not mvs:
        return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW
    elif len(mvs) == 1:
        return DirectByteStreamBufferView(mvs[0])
    else:
        return SegmentedByteStreamBufferView(mvs)


########################################
# ../../../logs/asyncs.py


##


class AsyncLoggerToLogger(Logger):
    def __init__(self, u: AsyncLogger) -> None:
        super().__init__()

        self._u = u

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        # Nope out early to avoid sync_await if possible - don't bother in the LoggerToAsyncLogger.
        if not self.is_enabled_for(ctx.must_get_info(LoggingContextInfos.Level).level):
            return

        # Note: we hardcode the stack offset of sync_await (which is 2 - sync_await + sync_await.thunk). In non-lite
        # code, lang.sync_await uses a cext if present to avoid being on the py stack, which would obviously complicate
        # this, but this is lite code so we will always have the non-c version.
        sync_await(
            self._u._log(  # noqa
                check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(3),
                msg,
                *args,
                **kwargs,
            ),
        )

    def _metric(self, m: LoggerMetric) -> None:
        sync_await(self._u._metric(m))  # noqa


class LoggerToAsyncLogger(AsyncLogger):
    def __init__(self, u: Logger) -> None:
        super().__init__()

        self._u = u

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self._u._log(  # noqa
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )

    async def _metric(self, m: LoggerMetric) -> None:
        self._u._metric(m)  # noqa


########################################
# ../../../logs/std/loggers.py


##


class StdLogger(Logger):
    def __init__(self, std: logging.Logger) -> None:
        super().__init__()

        self._std = std

    @property
    def std(self) -> logging.Logger:
        return self._std

    def is_enabled_for(self, level: LogLevel) -> bool:
        return self._std.isEnabledFor(level)

    def get_effective_level(self) -> LogLevel:
        return self._std.getEffectiveLevel()

    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
    ) -> None:
        if not self.is_enabled_for(ctx.must_get_info(LoggingContextInfos.Level).level):
            return

        ctx.set_basic(
            name=self._std.name,

            msg=msg,
            args=args,
        )

        ctx.capture()

        rec = LoggingContextLogRecord(_logging_context=ctx)

        self._std.handle(rec)

    def _metric(self, m: LoggerMetric) -> None:
        pass


########################################
# ../bytes/decoders.py
"""
TODO:
 - netty 'pending_removal' trick
"""


##


class UnicodeDecoderIoPipelineHandler(IoPipelineHandler):
    """bytes/view -> str (UTF-8, replacement)."""

    def __init__(
            self,
            encoding: str = 'utf-8',
            *,
            errors: ta.Literal['strict', 'ignore', 'replace'] = 'strict',
    ) -> None:
        super().__init__()

        self._encoding = encoding
        self._errors = errors

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if ByteStreamBuffers.can_bytes(msg):
            b = ByteStreamBuffers.to_bytes(msg)

            msg = b.decode(self._encoding, errors=self._errors)

        ctx.feed_in(msg)


##


class DelimiterFrameDecoderIoPipelineHandler(InboundBytesBufferingIoPipelineHandler):
    """
    bytes-like -> frames using longest-match delimiter semantics.

    TODO:
     - flow control, *or* replace with BytesToMessageDecoderIoPipelineHandler
    """

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
            max_buffer: ta.Optional[int] = None,
            buffer_chunk_size: int = 64 * 1024,
            on_incomplete_final: ta.Literal['allow', 'raise'] = 'allow',
    ) -> None:
        super().__init__()

        self._on_incomplete_final = on_incomplete_final

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_size=max_buffer,
            chunk_size=buffer_chunk_size,
        ))

        self._fr = LongestMatchDelimiterByteStreamFrameDecoder(
            delims,
            keep_ends=keep_ends,
            max_size=max_size,
        )

    def inbound_buffered_bytes(self) -> int:
        return len(self._buf)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.FinalInput):
            self._produce_frames(ctx, final=True)
            ctx.feed_in(msg)
            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        self._produce_frames(ctx)

    def _produce_frames(self, ctx: IoPipelineHandlerContext, *, final: bool = False) -> None:
        frames = self._fr.decode(self._buf, final=final)

        if final and len(self._buf):
            if (oif := self._on_incomplete_final) == 'allow':
                frames.append(self._buf.split_to(len(self._buf)))
            elif oif == 'raise':
                raise IncompleteDecodingIoPipelineError
            else:
                raise RuntimeError(f'unexpected on_incomplete_final: {oif!r}')

        for fr in frames:
            ctx.feed_in(fr)


##


class BytesToMessageDecoderIoPipelineHandler(IoPipelineHandler, Abstract):
    @abc.abstractmethod
    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            data: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        raise NotImplementedError

    #

    _called_decode: bool = False  # ~ `selfFiredChannelRead`
    _produced_messages: bool = False  # ~ `firedChannelRead`

    def _call_decode(
            self,
            ctx: IoPipelineHandlerContext,
            data: CanByteStreamBuffer,
            *,
            final: bool = False,
    ) -> None:
        self._called_decode = True

        out: ta.List[ta.Any] = []
        self._decode(ctx, data, out, final=final)

        if not out:
            return

        self._produced_messages = True

        for out_msg in out:
            ctx.feed_in(out_msg)

    #

    def _on_bytes_input(self, ctx: IoPipelineHandlerContext, data: CanByteStreamBuffer) -> None:
        check.arg(len(data) > 0)

        self._call_decode(ctx, data)

    def _on_flush_input(self, ctx: IoPipelineHandlerContext) -> None:
        if (
                self._called_decode and
                not self._produced_messages and
                not ctx.services[IoPipelineFlow].is_auto_read()
        ):
            ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

        self._called_decode = False
        self._produced_messages = False

        ctx.feed_in(IoPipelineFlowMessages.FlushInput())

    def _on_final_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalInput) -> None:
        self._call_decode(ctx, DirectByteStreamBuffer(b''), final=True)

        ctx.feed_in(msg)

    #

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.FlushInput):
            self._on_flush_input(ctx)

        elif isinstance(msg, IoPipelineMessages.FinalInput):
            self._on_final_input(ctx, msg)

        elif ByteStreamBuffers.can_bytes(msg):
            self._on_bytes_input(ctx, msg)

        else:
            ctx.feed_in(msg)


#


@ta.final
class FnBytesToMessageDecoderIoPipelineHandler(BytesToMessageDecoderIoPipelineHandler):
    class DecodeFn(ta.Protocol):
        def __call__(
                self,
                ctx: IoPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> None:
            ...

    def __init__(
            self,
            decode_fn: DecodeFn,
    ) -> None:
        super().__init__()

        self._decode_fn = decode_fn

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            buf: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        self._decode_fn(ctx, buf, out, final=final)


##


class BufferedBytesToMessageDecoderIoPipelineHandler(
    InboundBytesBufferingIoPipelineHandler,
    BytesToMessageDecoderIoPipelineHandler,
    Abstract,
):
    def __init__(
            self,
            *,
            max_buffer_size: ta.Optional[int] = None,
            buffer_chunk_size: int = 64 * 1024,
            scanning_buffer: bool = False,
    ) -> None:
        super().__init__()

        self._max_buffer_size = max_buffer_size
        self._buffer_chunk_size = buffer_chunk_size
        self._scanning_buffer = scanning_buffer

    #

    def inbound_buffered_bytes(self) -> int:
        if (buf := self._buf) is None:
            return 0
        return len(buf)

    _buf: ta.Optional[MutableByteStreamBuffer] = None

    def _new_buf(self) -> MutableByteStreamBuffer:
        buf: MutableByteStreamBuffer = SegmentedByteStreamBuffer(
            max_size=self._max_buffer_size,
            chunk_size=self._buffer_chunk_size,
        )

        if self._scanning_buffer:
            buf = ScanningByteStreamBuffer(buf)

        return buf

    #

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            data: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        if final:
            check.arg(len(data) == 0)

            if not isinstance(data, ByteStreamBuffer):
                data = DirectByteStreamBuffer(b'')

            self._decode_buffer(ctx, data, out, final=final)

            return

        check.arg(len(data) > 0)

        if (buf := self._buf) is None:
            buf = self._buf = self._new_buf()

        for seg in ByteStreamBuffers.iter_segments(data):
            buf.write(seg)

        self._decode_buffer(ctx, buf, out, final=final)

    #

    @abc.abstractmethod
    def _decode_buffer(
            self,
            ctx: IoPipelineHandlerContext,
            buf: ByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        raise NotImplementedError


########################################
# ../../../logs/modules.py


##


def _get_module_std_logger(mod_globals: ta.Mapping[str, ta.Any]) -> logging.Logger:
    return logging.getLogger(mod_globals.get('__name__'))


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> Logger:
    return StdLogger(_get_module_std_logger(mod_globals))


def get_module_async_logger(mod_globals: ta.Mapping[str, ta.Any]) -> AsyncLogger:
    return LoggerToAsyncLogger(get_module_logger(mod_globals))


def get_module_loggers(mod_globals: ta.Mapping[str, ta.Any]) -> ta.Tuple[Logger, AsyncLogger]:
    return (
        log := get_module_logger(mod_globals),
        LoggerToAsyncLogger(log),
    )


########################################
# ../drivers/asyncio.py
"""
TODO:
 - better driver impl
   - only ever call create_task at startup, never in inner loops
     - nothing ever does `asyncio.wait(...)`
   - dedicated read_task, flush_task, sched_task
     - read_task toggles back and forth between reading and waiting
   - main task only reads from command queue
 - asynclite?
"""


log, alog = get_module_loggers(globals())  # noqa


##


class AsyncioStreamIoPipelineDriver(Abstract):
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['AsyncioStreamIoPipelineDriver.Config']

        read_chunk_size: int = 64 * 1024
        write_chunk_max: ta.Optional[int] = None

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            spec: IoPipeline.Spec,
            reader: asyncio.StreamReader,
            writer: ta.Optional[asyncio.StreamWriter] = None,
            config: ta.Optional[Config] = None,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._reader = reader
        self._writer = writer
        if config is None:
            config = AsyncioStreamIoPipelineDriver.Config.DEFAULT
        self._config = config

        #

        self._shutdown_event = asyncio.Event()

        self._command_queue: asyncio.Queue[AsyncioStreamIoPipelineDriver._Command] = asyncio.Queue()

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    @property
    def pipeline(self) -> IoPipeline:
        return self._pipeline

    ##
    # init

    _sched: 'AsyncioStreamIoPipelineDriver._SchedulingService'

    _pipeline: IoPipeline

    _flow: ta.Optional[IoPipelineFlow]

    _command_handlers: ta.Mapping[ta.Type['AsyncioStreamIoPipelineDriver._Command'], ta.Callable[[ta.Any], ta.Awaitable[None]]]  # noqa
    _output_handlers: ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[None]]]

    async def _init(self) -> None:
        self._sched = self._SchedulingService(self)

        services = IoPipelineServices.of(self._spec.services)
        self._flow = services.find(IoPipelineFlow)

        self._command_handlers = self._build_command_handlers()
        self._output_handlers = self._build_output_handlers()

        #

        self._pipeline = IoPipeline(dc.replace(
            self._spec,
            metadata=(*self._spec.metadata, DriverIoPipelineMetadata(self)),
            services=(*self._spec.services, self._sched),
        ))

    def _is_auto_read(self) -> bool:
        return (flow := self._flow) is None or flow.is_auto_read()

    ##
    # async utils

    @staticmethod
    async def _cancel_tasks(
            *tasks: ta.Optional[asyncio.Task],
            check_running: bool = False,
    ) -> None:
        if check_running:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                return
            else:
                if not loop.is_running():
                    return

        #

        cts: ta.List[asyncio.Task] = []

        for t in tasks:
            if t is not None and not t.done():
                t.cancel()
                cts.append(t)

        if cts:
            await asyncio.gather(*cts, return_exceptions=True)

    #

    async def _close_writer(self) -> None:
        if self._writer is None:
            return

        try:
            self._writer.close()
            await self._writer.wait_closed()

        except Exception:  # noqa
            # Best effort; transport close errors aren't actionable at this layer.
            pass

        self._writer = None

    ##

    class _Command(Abstract):
        pass

    ##
    # feed in

    @dc.dataclass(frozen=True)
    class _FeedInCommand(_Command):
        msgs: ta.Sequence[ta.Any]

        fut: ta.Optional['asyncio.Future[None]'] = None

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}([{", ".join(map(repr, self.msgs))}])'

    async def _handle_command_feed_in(self, cmd: _FeedInCommand) -> None:
        async def _inner() -> None:
            self._pipeline.feed_in(*cmd.msgs)  # noqa

        if (fut := cmd.fut) is None:
            await self._do_with_pipeline(_inner)
            return

        try:
            await self._do_with_pipeline(_inner)
            fut.set_result(None)
        except BaseException as e:  # noqa
            fut.set_exception(e)
            raise

    async def feed_in(self, *msgs: ta.Any) -> None:
        check.state(not self._shutdown_event.is_set())

        fut: asyncio.Future[None] = asyncio.Future()
        self._command_queue.put_nowait(AsyncioStreamIoPipelineDriver._FeedInCommand(msgs, fut=fut))
        await fut

    def feed_in_nowait(self, *msgs: ta.Any) -> None:
        check.state(not self._shutdown_event.is_set())

        self._command_queue.put_nowait(AsyncioStreamIoPipelineDriver._FeedInCommand(msgs))

    ##
    # read completed

    class _ReadCompletedCommand(_Command):
        def __init__(self, data: ta.Union[bytes, ta.List[bytes]]) -> None:
            self._data = data

        def __repr__(self) -> str:
            return (
                f'{self.__class__.__name__}@{id(self):x}'
                f'({"[...]" if isinstance(self._data, list) else "..." if self._data is not None else ""})'
            )

        def data(self) -> ta.Sequence[bytes]:
            if isinstance(self._data, bytes):
                return [self._data]
            elif isinstance(self._data, list):
                return self._data
            else:
                raise TypeError(self._data)

    class _ReadCancelledCommand(_Command):
        pass

    _pending_completed_reads: ta.Optional[ta.List[_ReadCompletedCommand]] = None

    async def _handle_command_read_completed(self, cmd: _ReadCompletedCommand) -> None:
        if not (self._want_read or self._is_auto_read()):
            if (pl := self._pending_completed_reads) is None:
                pl = self._pending_completed_reads = []

            pl.append(cmd)
            return

        #

        eof = False

        in_msgs: ta.List[ta.Any] = []

        for b in cmd.data():
            check.state(not eof)
            if not b:
                eof = True
            else:
                in_msgs.append(b)

        if self._flow is not None:
            in_msgs.append(IoPipelineFlowMessages.FlushInput())

        if eof:
            self._has_read_eof = True

            in_msgs.append(IoPipelineMessages.FinalInput())

        #

        async def _inner() -> None:
            self._pipeline.feed_in(*in_msgs)

        await self._do_with_pipeline(_inner)

        #

        if eof:
            self._shutdown_event.set()

            await self._close_writer()

    ##
    # update want read

    class _UpdateWantReadCommand(_Command):
        pass

    _has_sent_update_want_read_command: bool = False

    async def _send_update_want_read_command(self) -> None:
        if self._has_sent_update_want_read_command:
            return

        self._has_sent_update_want_read_command = True
        await self._command_queue.put(AsyncioStreamIoPipelineDriver._UpdateWantReadCommand())

    _want_read = False

    _delay_sending_update_want_read_command = False

    async def _set_want_read(self, want_read: bool) -> None:
        if self._want_read == want_read:
            return

        self._want_read = want_read

        if not self._delay_sending_update_want_read_command:
            await self._send_update_want_read_command()

    async def _handle_command_update_want_read(self, cmd: _UpdateWantReadCommand) -> None:
        self._sent_update_want_read_command = False

        if self._want_read:
            if self._pending_completed_reads:
                in_cmd = AsyncioStreamIoPipelineDriver._ReadCompletedCommand([
                    b
                    for pcr_cmd in self._pending_completed_reads
                    for b in pcr_cmd.data()
                ])
                self._command_queue.put_nowait(in_cmd)
                self._pending_completed_reads = None

            self._ensure_read_task()

    _has_read_eof = False

    def _maybe_ensure_read_task(self) -> None:
        if not self._has_read_eof and (self._want_read or self._is_auto_read()):
            self._ensure_read_task()

    @abc.abstractmethod
    def _ensure_read_task(self) -> None:
        raise NotImplementedError

    ##
    # scheduling

    class _SchedulingService(IoPipelineScheduling, IoPipelineService):
        def __init__(self, d: 'AsyncioStreamIoPipelineDriver') -> None:
            super().__init__()

            self._d = d

            self._pending: ta.List[ta.Tuple[float, ta.Callable[[], None]]] = []
            self._tasks: ta.Set[asyncio.Task] = set()

        class _Handle(IoPipelineScheduling.Handle):
            def cancel(self) -> None:
                raise NotImplementedError

        def schedule(
                self,
                handler_ref: IoPipelineHandlerRef,
                delay_s: float,
                fn: ta.Callable[[], None],
        ) -> IoPipelineScheduling.Handle:
            self._pending.append((delay_s, fn))
            return self._Handle()

        def cancel_all(self, handler_ref: ta.Optional[IoPipelineHandlerRef] = None) -> None:
            raise NotImplementedError

        async def _task_body(self, delay: float, fn: ta.Callable[[], None]) -> None:
            await asyncio.sleep(delay)

            self._d._command_queue.put_nowait(AsyncioStreamIoPipelineDriver._ScheduledCommand(fn))  # noqa

        async def _flush_pending(self) -> None:
            if not (lst := self._pending):
                return

            for delay, fn in lst:
                self._tasks.add(asyncio.create_task(functools.partial(self._task_body, delay, fn)()))

            self._pending = []

    @dc.dataclass(frozen=True)
    class _ScheduledCommand(_Command):
        fn: ta.Callable[[], None]

    async def _handle_scheduled_command(self, cmd: _ScheduledCommand) -> None:
        async def _inner() -> None:
            with self._pipeline.enter():
                cmd.fn()

        await self._do_with_pipeline(_inner)

    # handlers

    def _build_command_handlers(self) -> ta.Mapping[ta.Type[_Command], ta.Callable[[ta.Any], ta.Awaitable[None]]]:
        return {
            AsyncioStreamIoPipelineDriver._FeedInCommand: self._handle_command_feed_in,
            AsyncioStreamIoPipelineDriver._ReadCompletedCommand: self._handle_command_read_completed,
            AsyncioStreamIoPipelineDriver._UpdateWantReadCommand: self._handle_command_update_want_read,
            AsyncioStreamIoPipelineDriver._ScheduledCommand: self._handle_scheduled_command,
        }

    async def _handle_command(self, cmd: _Command) -> None:
        log.debug(lambda: f'Handling command: {cmd!r}')

        try:
            fn = self._command_handlers[cmd.__class__]
        except KeyError:
            raise TypeError(f'Unknown command type: {cmd.__class__}') from None

        await fn(cmd)

    ##
    # output handling

    # lifecycle

    async def _handle_output_final_output(self, msg: IoPipelineMessages.FinalOutput) -> None:
        self._shutdown_event.set()

        await self._close_writer()

    # defer

    async def _handle_output_defer(self, msg: IoPipelineMessages.Defer) -> None:
        self._pipeline.run_deferred(msg)

    # data (special cased)

    async def _handle_output_bytes(self, msg: ta.Any) -> None:
        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._writer is not None and mv:
                self._writer.write(mv)

    # flow

    async def _handle_output_flush_output(self, msg: IoPipelineFlowMessages.FlushOutput) -> None:
        if self._writer is not None:
            await self._writer.drain()

    async def _handle_output_ready_for_input(self, msg: IoPipelineFlowMessages.ReadyForInput) -> None:
        await self._set_want_read(True)

    # async

    async def _handle_output_await(self, msg: AsyncIoPipelineMessages.Await) -> None:
        try:
            result = await msg.obj

        except Exception as e:  # noqa
            with self._pipeline.enter():
                msg.set_failed(e)

        else:
            with self._pipeline.enter():
                msg.set_succeeded(result)

    # handlers

    def _build_output_handlers(self) -> ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[None]]]:
        return {
            IoPipelineMessages.FinalOutput: self._handle_output_final_output,
            IoPipelineMessages.Defer: self._handle_output_defer,
            IoPipelineFlowMessages.FlushOutput: self._handle_output_flush_output,
            IoPipelineFlowMessages.ReadyForInput: self._handle_output_ready_for_input,
            AsyncIoPipelineMessages.Await: self._handle_output_await,
        }

    async def _handle_output(self, msg: ta.Any) -> None:
        log.debug(lambda: f'Handling output: {msg!r}')

        if ByteStreamBuffers.can_bytes(msg):
            await self._handle_output_bytes(msg)
            return

        try:
            fn = self._output_handlers[msg.__class__]
        except KeyError:
            raise TypeError(f'Unknown output type: {msg.__class__}') from None

        await fn(msg)

    # execution helpers

    async def _do_with_pipeline(self, fn: ta.Callable[[], ta.Awaitable[None]]) -> None:
        prev_want_read = self._want_read
        if not self._is_auto_read():
            self._want_read = False

        self._delay_sending_update_want_read_command = True
        try:
            await fn()

            await self._drain_pipeline_output()

        finally:
            self._delay_sending_update_want_read_command = False

        if self._shutdown_event.is_set():
            return

        await self._sched._flush_pending()  # noqa

        if self._want_read != prev_want_read:
            await self._send_update_want_read_command()

        self._maybe_ensure_read_task()

    async def _drain_pipeline_output(self) -> None:
        while (msg := self._pipeline.output.poll()) is not None:
            await self._handle_output(msg)

    ##
    # shutdown

    _shutdown_task: asyncio.Task

    async def _shutdown_task_main(self) -> None:
        await self._shutdown_event.wait()

    ##
    # main loop

    @abc.abstractmethod
    def _run(self) -> ta.Awaitable[None]:
        raise NotImplementedError

    @async_exception_logging(alog)
    async def run(self) -> None:
        try:
            self._shutdown_task  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('Already running')

        await self._init()

        self._shutdown_task = asyncio.create_task(self._shutdown_task_main())

        try:
            try:
                await self._run()

            finally:
                self._pipeline.destroy()

        finally:
            await self._cancel_tasks(self._shutdown_task, check_running=True)


##


class SimpleAsyncioStreamIoPipelineDriver(AsyncioStreamIoPipelineDriver):
    _read_task: ta.Optional[asyncio.Task] = None

    def _ensure_read_task(self) -> None:
        if self._read_task is not None or self._shutdown_event.is_set():
            return

        self._read_task = asyncio.create_task(self._reader.read(self._config.read_chunk_size))

        def _done(task: 'asyncio.Task[bytes]') -> None:
            check.state(task is self._read_task)
            self._read_task = None

            if self._shutdown_event.is_set():
                return

            cmd: AsyncioStreamIoPipelineDriver._Command
            eof = False
            try:
                data = task.result()

            except asyncio.CancelledError:
                cmd = AsyncioStreamIoPipelineDriver._ReadCancelledCommand()  # noqa

            else:
                cmd = AsyncioStreamIoPipelineDriver._ReadCompletedCommand(data)  # noqa
                eof = not data

            self._command_queue.put_nowait(cmd)

            # FIXME: disable? toggle? this pre-reads till told to stop to try to reduce stalling
            if not eof:
                self._maybe_ensure_read_task()

        self._read_task.add_done_callback(_done)

    #

    async def _run(self) -> None:
        self._maybe_ensure_read_task()

        #

        command_queue_task: ta.Optional[asyncio.Task[AsyncioStreamIoPipelineDriver._Command]] = None

        try:
            if not self._shutdown_event.is_set():
                await self._handle_command(AsyncioStreamIoPipelineDriver._FeedInCommand([  # noqa
                    IoPipelineMessages.InitialInput(),
                ]))

            while not self._shutdown_event.is_set():
                if command_queue_task is None:
                    command_queue_task = asyncio.create_task(self._command_queue.get())

                done, pending = await asyncio.wait(
                    [command_queue_task, self._shutdown_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                winner = done.pop()

                if self._shutdown_event.is_set() or winner is self._shutdown_task:
                    break

                elif winner is command_queue_task:
                    cmd = command_queue_task.result()
                    command_queue_task = None

                    await self._handle_command(cmd)

                    del cmd
                    command_queue_task = None

                else:
                    raise RuntimeError(f'Unexpected task: {winner!r}')
        #

        finally:
            await self._cancel_tasks(
                command_queue_task,
                self._read_task,
                check_running=True,
            )


########################################
# _amalg.py


# from .http.client.requests import PipelineHttpRequestEncoder  # noqa
# from .http.client.responses import PipelineHttpResponseDecoder  # noqa
# from .http.server.requests import PipelineHttpRequestDecoder  # noqa
# from .http.server.responses import PipelineHttpResponseEncoder  # noqa


##
