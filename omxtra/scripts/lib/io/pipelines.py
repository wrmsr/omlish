#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../../../io/pipelines/_amalg.py
# @omlish-git-diff-omit
# ruff: noqa: FURB188 PYI034 UP006 UP007 UP036 UP037 UP043 UP045 UP046
import abc
import asyncio
import collections
import collections.abc
import dataclasses as dc
import datetime
import enum
import functools
import http
import http.client
import inspect
import io
import logging
import os.path
import re
import sys
import threading
import time
import traceback
import types
import typing as ta
import zlib


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


def __omlish_amalg__():  # noqa
    return dict(
        src_files=[
            dict(path='../../../omlish/http/versions.py', sha1='5b1659b81eb197c6880fbe78684a1348595ec804'),
            dict(path='../../../omlish/io/streams/errors.py', sha1='67ca85fd8741b5bfefe76c872ce1c30c18fab06f'),
            dict(path='../../../omlish/lite/abstract.py', sha1='a2fc3f3697fa8de5247761e9d554e70176f37aac'),
            dict(path='../../../omlish/lite/asyncs.py', sha1='b3f2251c56617ce548abf9c333ac996b63edb23e'),
            dict(path='../../../omlish/lite/check.py', sha1='5e625d74d4ad4e0492e25acac42820baa9956965'),
            dict(path='../../../omlish/lite/dataclasses.py', sha1='8b144d1d9474d96cf2a35f4db5cb224c30f538d6'),
            dict(path='../../../omlish/lite/namespaces.py', sha1='27b12b6592403c010fb8b2a0af7c24238490d3a1'),
            dict(path='../../../omlish/logs/levels.py', sha1='91405563d082a5eba874da82aac89d83ce7b6152'),
            dict(path='../../../omlish/logs/warnings.py', sha1='c4eb694b24773351107fcc058f3620f1dbfb6799'),
            dict(path='errors.py', sha1='f0f9d973a1a219f790b309b043875b730b8863d4'),
            dict(path='../../../omlish/http/headers.py', sha1='a8204e05f535f04891ff4967f17332f4fad04f23'),
            dict(path='../../../omlish/http/parsing.py', sha1='2ee187993274e697332c7df7b46a98382f4cee2a'),
            dict(path='../../../omlish/io/streams/types.py', sha1='ab72e5d4a1e648ef79577be7d8c45853b1c5917d'),
            dict(path='../../../omlish/logs/infos.py', sha1='4dd104bd468a8c438601dd0bbda619b47d2f1620'),
            dict(path='../../../omlish/logs/metrics/base.py', sha1='95120732c745ceec5333f81553761ab6ff4bb3fb'),
            dict(path='../../../omlish/logs/protocols.py', sha1='05ca4d1d7feb50c4e3b9f22ee371aa7bf4b3dbd1'),
            dict(path='core.py', sha1='e1b46db31e8ed593e17e23ebb48fa28d729ab4fa'),
            dict(path='../../../omlish/io/streams/base.py', sha1='bdeaff419684dec34fd0dc59808a9686131992bc'),
            dict(path='../../../omlish/io/streams/framing.py', sha1='dc2d7f638b042619fd3d95789c71532a29fd5fe4'),
            dict(path='../../../omlish/io/streams/utils.py', sha1='476363dfce81e3177a66f066892ed3fcf773ead8'),
            dict(path='../../../omlish/logs/contexts.py', sha1='1000a6d5ddfb642865ca532e34b1d50759781cf0'),
            dict(path='../../../omlish/logs/utils.py', sha1='9b879044cbdc3172fd7282c7f2a4880b81261cdd'),
            dict(path='asyncs.py', sha1='3c5834fe4879ebdc63d44951798ad9110ae83ad4'),
            dict(path='bytes/buffering.py', sha1='aa8375c8ef0689db865bb4009afd3ed8dcc2bd12'),
            dict(path='flow/types.py', sha1='839f08718c67d2d84e56aee973ba1c9c34afb732'),
            dict(path='handlers/fns.py', sha1='75e982604574d6ffaacf9ac1f37ab6e9edbd608d'),
            dict(path='handlers/queues.py', sha1='73f018001a9e305194ed1bf9783fc49a71c2ed49'),
            dict(path='http/objects.py', sha1='f5da224c194ee16ebcc999970d2c97ce615f7e6e'),
            dict(path='sched/types.py', sha1='a443beb7866e5e019d57093225cd44b9ea5fa58e'),
            dict(path='../../../omlish/io/streams/direct.py', sha1='83c33460e9490a77a00ae66251617ba98128b56b'),
            dict(path='../../../omlish/io/streams/scanning.py', sha1='6ab39887d0d2d3002201b786c4715e64804c66c8'),
            dict(path='../../../omlish/logs/base.py', sha1='eaa2ce213235815e2f86c50df6c41cfe26a43ba2'),
            dict(path='../../../omlish/logs/std/records.py', sha1='67e552537d9268d4df6939b8a92be885fda35238'),
            dict(path='bytes/queues.py', sha1='38b11596cd0fa2367825252413923f1292c14f4e'),
            dict(path='handlers/flatmap.py', sha1='4e7f009885ee35e4746d14ba22f78d7b108f42c8'),
            dict(path='http/encoders.py', sha1='0659902d945aea54e367d04336792cccd4ed6374'),
            dict(path='http/requests.py', sha1='f518ff8896cbd01d30d58088d5b429f121c1c3e7'),
            dict(path='http/responses.py', sha1='f81688d98516bd81d2a22ba791c783404e806294'),
            dict(path='../../../omlish/io/streams/segmented.py', sha1='4aeb1c22b7b5994132f0b5906d70b3e53201776b'),
            dict(path='../../../omlish/logs/asyncs.py', sha1='8376df395029a9d0957e2338adede895a9364215'),
            dict(path='../../../omlish/logs/std/loggers.py', sha1='dbdfc66188e6accb75d03454e43221d3fba0f011'),
            dict(path='http/client/requests.py', sha1='0d598fefb873796d64f1fe1eafa344bda83d933c'),
            dict(path='http/server/responses.py', sha1='5b2e2af9bfdbd526f74cff138ddbb5bf03b4c0ee'),
            dict(path='../../../omlish/logs/modules.py', sha1='dd7d5f8e63fe8829dfb49460f3929ab64b68ee14'),
            dict(path='bytes/decoders.py', sha1='212e4f54b7bc55028ae75dfb75b3ec18cc5bad51'),
            dict(path='http/decoders.py', sha1='d82d2096b3016e84019bf723aeb17586e2472fd5'),
            dict(path='drivers/asyncio.py', sha1='af72109759129233c49f4f7a83ea60597d2d044a'),
            dict(path='http/client/responses.py', sha1='830f862d73a28624137f780ef5b02eccbaff38e6'),
            dict(path='http/server/requests.py', sha1='1007de97135c4712c67e5814cb17d7bc85650dad'),
            dict(path='_amalg.py', sha1='f66657d8b3801c6e8e84db2e4cd1b593d9e029be'),
        ],
    )


########################################


# ../../../omlish/lite/abstract.py
T = ta.TypeVar('T')

# ../../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# ../../../omlish/logs/levels.py
LogLevel = int  # ta.TypeAlias

# ../../../omlish/http/headers.py
StrOrBytes = ta.Union[str, bytes]  # ta.TypeAlias

# ../../../omlish/io/streams/types.py
BytesLikeOrMemoryview = ta.Union[bytes, bytearray, memoryview]  # ta.TypeAlias

# ../../../omlish/logs/infos.py
LoggingMsgFn = ta.Callable[[], ta.Union[str, tuple]]  # ta.TypeAlias
LoggingExcInfoTuple = ta.Tuple[ta.Type[BaseException], BaseException, ta.Optional[types.TracebackType]]  # ta.TypeAlias
LoggingExcInfo = ta.Union[BaseException, LoggingExcInfoTuple]  # ta.TypeAlias
LoggingExcInfoArg = ta.Union[LoggingExcInfo, bool, None]  # ta.TypeAlias
LoggingContextInfo = ta.Any  # ta.TypeAlias

# core.py
F = ta.TypeVar('F')
ChannelPipelineHandlerFn = ta.Callable[['ChannelPipelineHandlerContext', F], T]  # ta.TypeAlias
ChannelPipelineHandlerT = ta.TypeVar('ChannelPipelineHandlerT', bound='ChannelPipelineHandler')
ShareableChannelPipelineHandlerT = ta.TypeVar('ShareableChannelPipelineHandlerT', bound='ShareableChannelPipelineHandler')  # noqa
PipelineChannelMetadataT = ta.TypeVar('PipelineChannelMetadataT', bound='PipelineChannelMetadata')

# ../../../omlish/logs/contexts.py
LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)


########################################
# ../../../../omlish/http/versions.py


##


class UnknownHttpVersionError(Exception):
    pass


@ta.final
@functools.total_ordering
class HttpVersion:
    def __init__(self, major: int, minor: int) -> None:
        self._major = major
        self._minor = minor

        self._parts = parts = (major, minor)

        self._hash = hash(parts)

        self._str = f'HTTP/{major}.{minor}'
        self._short_str = f'{major}.{minor}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.major}, {self.minor})'

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> ta.Any:
        if not isinstance(other, HttpVersion):
            return NotImplemented
        return self._parts == other._parts

    def __lt__(self, other: object) -> ta.Any:
        if not isinstance(other, HttpVersion):
            return NotImplemented
        return self._parts < other._parts

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    def __str__(self) -> str:
        return self._str

    @property
    def short_str(self) -> str:
        return self._short_str

    def __iter__(self) -> ta.Iterator[int]:
        return iter(self._parts)


@ta.final
class HttpVersions:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    HTTP_0_9 = HttpVersion(0, 9)
    HTTP_1_0 = HttpVersion(1, 0)
    HTTP_1_1 = HttpVersion(1, 1)
    HTTP_2_0 = HttpVersion(2, 0)

    _FROM_STR: ta.ClassVar[ta.Mapping[str, HttpVersion]] = {
        str(v): v for v in [
            HTTP_0_9,
            HTTP_1_0,
            HTTP_1_1,
            HTTP_2_0,
        ]
    }

    @classmethod
    def from_str(cls, s: str) -> HttpVersion:
        try:
            return cls._FROM_STR[s]
        except KeyError:
            raise UnknownHttpVersionError(s) from None

    @classmethod
    def of(cls, o: ta.Union[HttpVersion, str]) -> HttpVersion:
        if isinstance(o, HttpVersion):
            return o
        elif isinstance(o, str):
            return cls.from_str(o)
        else:
            raise TypeError(o)


########################################
# ../../../../omlish/io/streams/errors.py


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
# ../../../../omlish/lite/abstract.py


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
# ../../../../omlish/lite/asyncs.py


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
# ../../../../omlish/lite/check.py
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
        exc_args = ()
        if callable(message):
            message = ta.cast(ta.Callable, message)(*ak.args, **ak.kwargs)
            if isinstance(message, tuple):
                message, *exc_args = message  # type: ignore

        if message is None:
            message = default_message

        self._late_configure()

        if render_fmt is not None and (af := self._args_renderer) is not None:
            rendered_args = af(render_fmt, *ak.args)
            if rendered_args is not None:
                message = f'{message} : {rendered_args}'

        exc = self._exception_factory(
            exception_type,
            message,
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
        if not isinstance(v, spec if type(spec) is type else self._unpack_isinstance_spec(spec)):
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
        spec = spec if type(spec) is type else self._unpack_isinstance_spec(spec)

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
        if isinstance(v, spec if type(spec) is type else self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must not be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='isinstance(%s, %s)',
            )

        return v

    def of_not_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        spec = spec if type(spec) is type else self._unpack_isinstance_spec(spec)

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
                Checks._ArgsKwargs(v),
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
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

    def state(self, v: bool, msg: CheckMessage = None, /) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'State condition not met',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )


check = Checks()


########################################
# ../../../../omlish/lite/dataclasses.py


##


def dataclass_shallow_astuple(o: ta.Any) -> ta.Tuple[ta.Any, ...]:
    return tuple(getattr(o, f.name) for f in dc.fields(o))


def dataclass_shallow_asdict(o: ta.Any) -> ta.Dict[str, ta.Any]:
    return {f.name: getattr(o, f.name) for f in dc.fields(o)}


##


def is_immediate_dataclass(cls: type) -> bool:
    if not isinstance(cls, type):
        raise TypeError(cls)
    return dc._FIELDS in cls.__dict__  # type: ignore[attr-defined]  # noqa


##


def _install_dataclass_fn(cls: type, fn: ta.Any, fn_name: ta.Optional[str] = None) -> None:
    if fn_name is None:
        fn_name = fn.__name__
    setattr(cls, fn_name, fn)
    fn.__qualname__ = f'{cls.__qualname__}.{fn_name}'


##


def install_dataclass_cache_hash(
        *,
        cached_hash_attr: str = '__dataclass_hash__',
):
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        if (
                cls.__hash__ is object.__hash__ or
                '__hash__' not in cls.__dict__
        ):
            raise TypeError(cls)

        real_hash = cls.__hash__

        def cached_hash(self) -> int:
            try:
                return object.__getattribute__(self, cached_hash_attr)
            except AttributeError:
                object.__setattr__(self, cached_hash_attr, h := real_hash(self))  # type: ignore[call-arg]
            return h

        _install_dataclass_fn(cls, cached_hash, '__hash__')

        return cls

    return inner


##


def dataclass_maybe_post_init(sup: ta.Any) -> bool:
    if not isinstance(sup, super):
        raise TypeError(sup)
    try:
        fn = sup.__post_init__  # type: ignore
    except AttributeError:
        return False
    fn()
    return True


##


def dataclass_filtered_repr(
        obj: ta.Any,
        fn: ta.Union[ta.Callable[[ta.Any, dc.Field, ta.Any], bool], ta.Literal['omit_none', 'omit_falsey']],
) -> str:
    if fn == 'omit_none':
        fn = lambda o, f, v: v is not None  # noqa
    elif fn == 'omit_falsey':
        fn = lambda o, f, v: bool(v)

    return (
        f'{obj.__class__.__qualname__}(' +
        ', '.join([
            f'{f.name}={v!r}'
            for f in dc.fields(obj)
            if fn(obj, f, v := getattr(obj, f.name))
        ]) +
        ')'
    )


def dataclass_repr_omit_none(obj: ta.Any) -> str:
    return dataclass_filtered_repr(obj, 'omit_none')


def dataclass_repr_omit_falsey(obj: ta.Any) -> str:
    return dataclass_filtered_repr(obj, 'omit_falsey')


def install_dataclass_filtered_repr(
        fn: ta.Union[ta.Callable[[ta.Any, dc.Field, ta.Any], bool], ta.Literal['omit_none', 'omit_falsey']],
):
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        def filtered_repr(self) -> str:
            return dataclass_filtered_repr(self, fn)

        _install_dataclass_fn(cls, filtered_repr, '__repr__')

        return cls

    return inner


#


def dataclass_terse_repr(obj: ta.Any) -> str:
    return f'{obj.__class__.__qualname__}({", ".join(repr(getattr(obj, f.name)) for f in dc.fields(obj))})'


def install_dataclass_terse_repr():
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        def terse_repr(self) -> str:
            return dataclass_terse_repr(self)

        _install_dataclass_fn(cls, terse_repr, '__repr__')

        return cls

    return inner


##


def dataclass_descriptor_method(*bind_attrs: str, bind_owner: bool = False) -> ta.Callable:
    if not bind_attrs:
        def __get__(self, instance, owner=None):  # noqa
            return self

    elif bind_owner:
        def __get__(self, instance, owner=None):  # noqa
            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    else:
        def __get__(self, instance, owner=None):  # noqa
            if instance is None:
                return self

            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    return __get__


##


def install_dataclass_kw_only_init():
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        real_init = cls.__init__  # type: ignore[misc]

        flds = dc.fields(cls)  # noqa

        if any(f.name == 'self' for f in flds):
            self_name = '__dataclass_self__'
        else:
            self_name = 'self'

        src = '\n'.join([
            'def __init__(',
            f'    {self_name},',
            '    *,',
            *[
                ''.join([
                    f'    {f.name}: __dataclass_type_{f.name}__',
                    f' = __dataclass_default_{f.name}__' if f.default is not dc.MISSING else '',
                    ',',
                ])
                for f in flds
            ],
            ') -> __dataclass_None__:',
            '    __dataclass_real_init__(',
            f'        {self_name},',
            *[
                f'        {f.name}={f.name},'
                for f in flds
            ],
            '    )',
        ])

        ns: dict = {
            '__dataclass_None__': None,
            '__dataclass_real_init__': real_init,
            **{
                f'__dataclass_type_{f.name}__': f.type
                for f in flds
            },
            **{
                f'__dataclass_default_{f.name}__': f.default
                for f in flds
                if f.default is not dc.MISSING
            },
        }

        exec(src, ns)

        kw_only_init = ns['__init__']

        functools.update_wrapper(kw_only_init, real_init)

        _install_dataclass_fn(cls, kw_only_init, '__init__')

        return cls

    return inner


##


@dc.dataclass()
class DataclassFieldRequiredError(Exception):
    name: str


def dataclass_field_required(name: str) -> ta.Callable[[], ta.Any]:
    def inner() -> ta.NoReturn:
        raise DataclassFieldRequiredError(name)
    return inner


########################################
# ../../../../omlish/lite/namespaces.py


class NamespaceClass:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    def __init_subclass__(cls, **kwargs):  # noqa
        super().__init_subclass__(**kwargs)

        if any(issubclass(b, NamespaceClass) and b is not NamespaceClass for b in cls.__bases__):
            raise TypeError


########################################
# ../../../../omlish/logs/levels.py


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
# ../../../../omlish/logs/warnings.py


##


class LoggingSetupWarning(Warning):
    pass


########################################
# ../errors.py


##


class ChannelPipelineError(Exception):
    pass


##


class UnhandleableChannelPipelineError(ChannelPipelineError):
    pass


##
# state


class ContextInvalidatedChannelPipelineError(ChannelPipelineError):
    pass


class SawFinalInputChannelPipelineError(ChannelPipelineError):
    pass


class FinalOutputChannelPipelineError(ChannelPipelineError):
    pass


##
# messages


@dc.dataclass()
class MessageChannelPipelineError(ChannelPipelineError):
    inbound: ta.Optional[ta.Sequence[ta.Any]] = None
    outbound: ta.Optional[ta.Sequence[ta.Any]] = None

    def __repr__(self) -> str:
        return ''.join([
            f'{self.__class__.__name__}(',
            ', '.join([
                *([f'inbound={self.inbound!r}'] if self.inbound is not None else []),
                *([f'outbound={self.outbound!r}'] if self.outbound is not None else []),
            ]),
            ')',
        ])


@dc.dataclass()
class MessageNotPropagatedChannelPipelineError(MessageChannelPipelineError, UnhandleableChannelPipelineError):
    pass


@dc.dataclass()
class MessageReachedTerminalChannelPipelineError(MessageChannelPipelineError, UnhandleableChannelPipelineError):
    pass


##
# misc (TODO: move/cleanup)


class DecodingChannelPipelineError(ChannelPipelineError):
    pass


class IncompleteDecodingChannelPipelineError(DecodingChannelPipelineError):
    pass


class FlowControlValidationChannelPipelineError(ChannelPipelineError):
    pass


########################################
# ../../../../omlish/http/headers.py
"""
TODO:
 - handle secrets (but they're strs..)
"""


##


CanHttpHeaders = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'HttpHeaders',

    http.client.HTTPMessage,

    ta.Mapping[str, ta.Union[StrOrBytes, ta.Sequence[StrOrBytes]]],
    ta.Mapping[bytes, ta.Union[StrOrBytes, ta.Sequence[StrOrBytes]]],
    ta.Mapping[StrOrBytes, ta.Union[StrOrBytes, ta.Sequence[StrOrBytes]]],

    ta.Sequence[ta.Tuple[StrOrBytes, StrOrBytes]],
]


@dc.dataclass()
class DuplicateHttpHeaderError(Exception):
    key: str


class HttpHeaders(ta.Mapping[str, ta.Sequence[str]]):
    def __init__(self, src: CanHttpHeaders) -> None:
        super().__init__()

        if isinstance(src, HttpHeaders):
            check.is_(src, self)
            return

        raw: ta.List[ta.Tuple[str, str]] = []

        if isinstance(src, http.client.HTTPMessage):
            raw = list(src.items())

        elif isinstance(src, collections.abc.Mapping):
            for k, v in src.items():
                if isinstance(v, (str, bytes)):
                    raw.append((self._decode(k), self._decode(v)))
                else:
                    for e in v:
                        raw.append((self._decode(k), self._decode(e)))

        elif isinstance(src, (str, bytes)):  # type: ignore
            raise TypeError(src)

        elif isinstance(src, collections.abc.Sequence):
            for t in src:
                if isinstance(t, (str, bytes)):
                    raise TypeError(t)

                k, v = t
                raw.append((self._decode(k), self._decode(v)))

        else:
            raise TypeError(src)

        self._raw = raw

        self._all = tuple((self._as_key(k), v) for k, v in self._raw)

        dct: ta.Dict[str, ta.List[str]] = {}
        for k, v in self._all:
            dct.setdefault(k, []).append(v)
        self._dct = {k: tuple(v) for k, v in dct.items()}

    def __new__(cls, obj: CanHttpHeaders) -> 'HttpHeaders':
        if isinstance(obj, HttpHeaders):
            return obj

        return super().__new__(cls)

    #

    @property
    def raw(self) -> ta.Sequence[ta.Tuple[str, str]]:
        return self._raw

    @property
    def all(self) -> ta.Sequence[ta.Tuple[str, str]]:
        return self._all

    #

    @classmethod
    def _decode(cls, o: StrOrBytes) -> str:
        if isinstance(o, bytes):
            return o.decode('latin-1')
        elif isinstance(o, str):
            return o
        else:
            raise TypeError(o)

    @classmethod
    def _as_key(cls, o: StrOrBytes) -> str:
        return cls._decode(o).lower()

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._raw!r})'

    #

    def __bool__(self) -> bool:
        return len(self._dct) > 0

    #

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self._dct)

    def __getitem__(self, key: str) -> ta.Sequence[str]:
        return self._dct[key.lower()]

    #

    @ta.final
    class _SingleAccessor:
        def __init__(self, o: 'HttpHeaders') -> None:
            self._o = o

        def __getitem__(self, key: str) -> str:
            l = self._o._dct[key.lower()]  # noqa
            if len(l) > 1:
                raise DuplicateHttpHeaderError(key)
            return l[0]

        @ta.overload
        def get(self, key: str, /, default: str) -> str:
            ...

        @ta.overload
        def get(self, key: str, /, default: ta.Optional[str] = None) -> ta.Optional[str]:
            ...

        def get(self, key, /, default=None):
            try:
                return self[key]
            except KeyError:
                return default

    _single: _SingleAccessor

    @property
    def single(self) -> _SingleAccessor:
        try:
            return self._single
        except AttributeError:
            pass
        a = self._single = self._SingleAccessor(self)
        return a

    #

    @ta.final
    class _LowerAccessor:
        def __init__(self, o: 'HttpHeaders') -> None:
            self._o = o

            self._cache: ta.Dict[str, ta.Sequence[str]] = {}

        def __getitem__(self, key: str) -> ta.Sequence[str]:
            key = key.lower()
            try:
                return self._cache[key]
            except KeyError:
                pass
            x = self._o._dct[key]  # noqa
            l = self._cache[key] = tuple(v.lower() for v in x)
            return l

        @ta.overload
        def get(self, key: str, /, default: ta.Sequence[str]) -> ta.Sequence[str]:
            ...

        @ta.overload
        def get(self, key: str, /, default: ta.Optional[str] = None) -> ta.Optional[ta.Sequence[str]]:
            ...

        def get(self, key, /, default=None):
            try:
                return self[key]
            except KeyError:
                return default

    _lower: _LowerAccessor

    @property
    def lower(self) -> _LowerAccessor:
        try:
            return self._lower
        except AttributeError:
            pass
        a = self._lower = self._LowerAccessor(self)
        return a

    #

    def contains_value(self, key: str, value: str, *, ignore_case: bool = False) -> bool:
        try:
            if ignore_case:
                vs = self.lower[key.lower()]
            else:
                vs = self._dct[key.lower()]
        except KeyError:
            return False
        return value in vs

    def update(
            self,
            *items: ta.Tuple[str, str],
            override: bool = False,
    ) -> 'HttpHeaders':
        if override:
            nks = {self._as_key(k) for k, v in items}
            src = [(k, v) for k, v in self._raw if k.lower() not in nks]
        else:
            src = list(self._raw)
        return HttpHeaders([
            *src,
            *items,
        ])


########################################
# ../../../../omlish/http/parsing.py
"""
Parses a complete HTTP/1.x start-line + header fields + final CRLF from a ``bytes`` object. Does NOT handle message
bodies, chunked transfer decoding, trailers, or HTTP/2+.

TODO:
 - mapping from error code to outbound http status code
"""


##


class StartLineHttpParseErrorCode(enum.Enum):
    MALFORMED_REQUEST_LINE = enum.auto()
    MALFORMED_STATUS_LINE = enum.auto()
    UNSUPPORTED_HTTP_VERSION = enum.auto()
    INVALID_METHOD = enum.auto()
    INVALID_REQUEST_TARGET = enum.auto()
    INVALID_STATUS_CODE = enum.auto()


class HeaderFieldHttpParseErrorCode(enum.Enum):
    INVALID_FIELD_NAME = enum.auto()
    INVALID_FIELD_VALUE = enum.auto()
    OBS_FOLD_NOT_ALLOWED = enum.auto()
    SPACE_BEFORE_COLON = enum.auto()
    MISSING_COLON = enum.auto()
    BARE_CARRIAGE_RETURN = enum.auto()
    BARE_LF = enum.auto()
    NUL_IN_HEADER = enum.auto()
    MISSING_TERMINATOR = enum.auto()
    TRAILING_DATA = enum.auto()
    TOO_MANY_HEADERS = enum.auto()
    EMPTY_FIELD_NAME = enum.auto()


class SemanticHeaderHttpParseErrorCode(enum.Enum):
    DUPLICATE_CONTENT_LENGTH = enum.auto()
    CONFLICTING_CONTENT_LENGTH = enum.auto()
    CONTENT_LENGTH_WITH_TRANSFER_ENCODING = enum.auto()
    MISSING_HOST_HEADER = enum.auto()
    MULTIPLE_HOST_HEADERS = enum.auto()
    CONFLICTING_HOST_HEADERS = enum.auto()
    INVALID_CONTENT_LENGTH = enum.auto()
    INVALID_TRANSFER_ENCODING = enum.auto()
    INVALID_CONTENT_TYPE = enum.auto()
    FORBIDDEN_TRAILER_FIELD = enum.auto()
    INVALID_HOST = enum.auto()
    INVALID_EXPECT = enum.auto()
    INVALID_DATE = enum.auto()
    INVALID_CACHE_CONTROL = enum.auto()
    INVALID_ACCEPT_ENCODING = enum.auto()
    INVALID_ACCEPT = enum.auto()
    INVALID_AUTHORIZATION = enum.auto()
    TE_WITHOUT_CHUNKED_LAST = enum.auto()
    TE_IN_HTTP10 = enum.auto()


class EncodingHttpParseErrorCode(enum.Enum):
    NON_ASCII_IN_FIELD_NAME = enum.auto()
    OBS_TEXT_IN_FIELD_VALUE = enum.auto()


HttpParseErrorCode = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    StartLineHttpParseErrorCode,
    HeaderFieldHttpParseErrorCode,
    SemanticHeaderHttpParseErrorCode,
    EncodingHttpParseErrorCode,
]


##


class HttpParseError(Exception):
    pass


@dc.dataclass()
class ErrorCodeHttpParseError(HttpParseError):
    """Base exception for all HTTP header parsing errors."""

    code: HttpParseErrorCode
    message: str = ''
    line: int = 0
    offset: int = 0

    def __post_init__(self) -> None:
        Exception.__init__(self, str(self))

    def __str__(self) -> str:
        return f'[{self.code.name}] line {self.line}, offset {self.offset}: {self.message}'


@dc.dataclass()
class StartLineHttpParseError(ErrorCodeHttpParseError):
    """Errors in the request-line or status-line."""

    code: StartLineHttpParseErrorCode = dc.field(default=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE)


@dc.dataclass()
class HeaderFieldHttpParseError(ErrorCodeHttpParseError):
    """Errors in header field syntax."""

    code: HeaderFieldHttpParseErrorCode = dc.field(default=HeaderFieldHttpParseErrorCode.INVALID_FIELD_NAME)


@dc.dataclass()
class SemanticHeaderHttpParseError(ErrorCodeHttpParseError):
    """Errors in header field semantics / cross-field validation."""

    code: SemanticHeaderHttpParseErrorCode = dc.field(default=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH)


@dc.dataclass()
class EncodingHttpParseError(ErrorCodeHttpParseError):
    """Errors in character encoding within headers."""

    code: EncodingHttpParseErrorCode = dc.field(default=EncodingHttpParseErrorCode.NON_ASCII_IN_FIELD_NAME)


@dc.dataclass()
class NoCombineHeaderHttpParseError(HttpParseError):
    """Errors in headers where duplicate values are not allowed."""

    name: str


##


@ta.final
class ParsedHttpHeaders:
    """
    Normalized, case-insensitive header mapping.

    Field names are stored in lowercase. Values are decoded as Latin-1. Multiple values for the same field-name are
    stored individually and combined with ``", "`` on access (except Set-Cookie, which is never combined).
    """

    def __init__(self) -> None:
        # normalized name -> list of individual values
        self._entries: ta.Dict[str, ta.List[str]] = {}

        # insertion-ordered unique names
        self._order: ta.List[str] = []

    def _add(self, name: str, value: str) -> None:
        if name not in self._entries:
            self._entries[name] = []
            self._order.append(name)
        self._entries[name].append(value)

    @property
    def entries(self) -> ta.Mapping[str, ta.Sequence[str]]:
        return self._entries

    def __contains__(self, name: ta.Any) -> bool:
        if not isinstance(name, str):
            return False
        return name.lower() in self._entries

    # Headers where duplicate values are comma-combined per RFC 7230 §3.2.2. Set-Cookie is the notable exception.
    _NO_COMBINE_HEADERS: ta.ClassVar[ta.FrozenSet[str]] = frozenset({
        'set-cookie',
    })

    def __getitem__(self, name: str) -> str:
        key = name.lower()
        values = self._entries[key]
        if key in self._NO_COMBINE_HEADERS:
            raise NoCombineHeaderHttpParseError(name)
        return ', '.join(values)

    def get(self, name: str, default: ta.Optional[str] = None) -> ta.Optional[str]:
        try:
            return self[name]
        except KeyError:
            return default

    def get_all(self, name: str) -> ta.List[str]:
        return list(self._entries.get(name.lower(), []))

    def items(self) -> ta.List[ta.Tuple[str, str]]:
        result: ta.List[ta.Tuple[str, str]] = []
        for name in self._order:
            values = self._entries[name]
            if name in self._NO_COMBINE_HEADERS:
                for v in values:
                    result.append((name, v))
            else:
                result.append((name, ', '.join(values)))
        return result

    def keys(self) -> ta.List[str]:
        return list(self._order)

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self._order)

    def __len__(self) -> int:
        return len(self._order)

    def __repr__(self) -> str:
        return f'ParsedHttpHeaders({dict(self.items())})'


@dc.dataclass()
class PreparedParsedHttpHeaders:
    content_length: ta.Optional[int] = None

    transfer_encoding: ta.Optional[ta.List[str]] = None

    host: ta.Optional[str] = None

    connection: ta.Optional[ta.FrozenSet[str]] = None
    keep_alive: ta.Optional[bool] = None

    @dc.dataclass(frozen=True)
    class ContentType:
        media_type: str
        params: ta.Dict[str, str]

        @property
        def charset(self) -> ta.Optional[str]:
            return self.params.get('charset')

    content_type: ta.Optional[ContentType] = None

    te: ta.Optional[ta.List[str]] = None

    upgrade: ta.Optional[ta.List[str]] = None

    trailer: ta.Optional[ta.FrozenSet[str]] = None

    expect: ta.Optional[str] = None
    expect_100_continue: ta.Optional[bool] = None

    date: ta.Optional[datetime.datetime] = None

    cache_control: ta.Optional[ta.Dict[str, ta.Optional[str]]] = None

    @dc.dataclass(frozen=True)
    class AcceptEncodingItem:
        coding: str
        q: float = 1.0

    accept_encoding: ta.Optional[ta.List[AcceptEncodingItem]] = None

    @dc.dataclass(frozen=True)
    class AcceptItem:
        media_range: str
        q: float = 1.0
        params: ta.Dict[str, str] = dc.field(default_factory=dict)

    accept: ta.Optional[ta.List[AcceptItem]] = None

    @dc.dataclass(frozen=True)
    class AuthorizationValue:
        scheme: str
        credentials: str

    authorization: ta.Optional[AuthorizationValue] = None

    def __repr__(self) -> str:
        return ''.join([
            f'{self.__class__.__name__}(',
            ', '.join([
                f'{f.name}={v!r}'
                for f in dc.fields(self)
                if (v := getattr(self, f.name) is not None)
            ]),
            ')',
        ])


@dc.dataclass(frozen=True)
class RawParsedHttpHeader:
    name: bytes
    value: bytes

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r}, {self.value!r})'


@dc.dataclass()
class ParsedHttpMessage:
    class Kind(enum.Enum):
        REQUEST = 'request'
        RESPONSE = 'response'

    kind: Kind

    @dc.dataclass(frozen=True)
    class RequestLine:
        method: str
        request_target: bytes
        http_version: HttpVersion

    request_line: ta.Optional[RequestLine]

    @dc.dataclass(frozen=True)
    class StatusLine:
        http_version: HttpVersion
        status_code: int
        reason_phrase: str

    status_line: ta.Optional[StatusLine]

    raw_headers: ta.List[RawParsedHttpHeader]
    headers: ParsedHttpHeaders

    prepared: PreparedParsedHttpHeaders


@dc.dataclass(frozen=True)
class ParsedHttpTrailers:
    """Result of parsing HTTP trailer fields."""

    raw_headers: ta.List[RawParsedHttpHeader]
    headers: ParsedHttpHeaders


##


class HttpParser:
    """Strict HTTP/1.x parser."""

    @dc.dataclass(frozen=True)
    class Config:
        """Strictness knobs. Defaults are maximally strict."""

        allow_obs_fold: bool = False
        allow_space_before_colon: bool = False  # DANGEROUS - upstreams may not handle well
        allow_multiple_content_lengths: bool = False
        allow_content_length_with_te: bool = False
        allow_bare_lf: bool = False
        allow_missing_host: bool = False
        allow_multiple_hosts: bool = False
        allow_unknown_transfer_encoding: bool = False
        allow_empty_header_values: bool = True
        allow_bare_cr_in_value: bool = False
        allow_te_without_chunked_in_response: bool = False
        allow_transfer_encoding_http10: bool = False
        reject_multi_value_content_length: bool = False
        reject_obs_text: bool = False
        reject_non_visible_ascii_request_target: bool = False
        max_header_count: int = 128
        max_header_length: ta.Optional[int] = 8192
        max_content_length_str_len: ta.Optional[int] = None

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    # Public API

    class Mode(enum.Enum):
        REQUEST = 'request'
        RESPONSE = 'response'
        AUTO = 'auto'

    def parse_message(self, data: bytes, mode: Mode = Mode.AUTO) -> ParsedHttpMessage:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f'Expected bytes, got {type(data).__name__}')

        ctx = _HttpParseContext(
            data=bytes(data),
            config=self._config,
            mode=mode,
        )

        # 1. Verify terminator
        ctx.verify_terminator()

        # 2. Split off start-line
        start_line_end = ctx.find_line_end(0)
        start_line_bytes = data[:start_line_end]

        # 3. Determine message kind
        kind = ctx.detect_kind(start_line_bytes)

        # 4. Parse start-line
        request_line: ta.Optional[ParsedHttpMessage.RequestLine] = None
        status_line: ta.Optional[ParsedHttpMessage.StatusLine] = None
        if kind == ParsedHttpMessage.Kind.REQUEST:
            request_line = ctx.parse_request_line(start_line_bytes)
        else:
            status_line = ctx.parse_status_line(start_line_bytes)

        http_version = (
            request_line.http_version if request_line else
            status_line.http_version if status_line else
            HttpVersions.HTTP_1_1
        )

        # 5. Parse header fields
        # Position after start-line CRLF (or LF if bare LF allowed)
        header_start = start_line_end + ctx.line_ending_len(start_line_end)
        raw_headers = ctx.parse_header_fields(header_start)

        # 6. Build normalized headers
        headers = ParsedHttpHeaders()
        for rh in raw_headers:
            name_str = rh.name.decode('ascii').lower()
            value_str = rh.value.decode('latin-1')
            headers._add(name_str, value_str)  # noqa

        # 7. Build prepared headers
        prepared = ctx.prepare_headers(headers, kind, http_version)

        return ParsedHttpMessage(
            kind=kind,
            request_line=request_line,
            status_line=status_line,
            raw_headers=raw_headers,
            headers=headers,
            prepared=prepared,
        )

    def parse_trailers(
        self,
        data: bytes,
    ) -> ParsedHttpTrailers:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f'Expected bytes, got {type(data).__name__}')

        # Special case: empty trailers (just the terminating empty line, no fields)
        if data == b'\r\n' or (self._config.allow_bare_lf and data == b'\n'):
            return ParsedHttpTrailers(
                raw_headers=[],
                headers=ParsedHttpHeaders(),
            )

        ctx = _HttpParseContext(
            data=bytes(data),
            config=self._config,
            mode=HttpParser.Mode.AUTO,
        )

        # Verify terminator (trailers end with an empty CRLF line, same as headers)
        ctx.verify_terminator()

        # Parse fields starting at position 0 (no start-line)
        raw_headers = ctx.parse_header_fields(0)

        # Build normalized headers
        headers = ParsedHttpHeaders()
        for rh in raw_headers:
            name_str = rh.name.decode('ascii').lower()
            value_str = rh.value.decode('latin-1')
            headers._add(name_str, value_str)  # noqa

        # Enforce forbidden trailer fields (RFC 7230 §4.1.2)
        for name in headers:
            if name in _HttpParseContext._FORBIDDEN_TRAILER_FIELDS:  # noqa
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.FORBIDDEN_TRAILER_FIELD,
                    message=f'Forbidden field in trailers: {name!r}',
                )

        return ParsedHttpTrailers(
            raw_headers=raw_headers,
            headers=headers,
        )


class _HttpParseContext:
    def __init__(
            self,
            data: bytes,
            config: HttpParser.Config,
            mode: HttpParser.Mode,
    ) -> None:
        super().__init__()

        self.data = data
        self.config = config
        self.mode = mode
        self.current_line = 0  # 0-indexed logical line number

    # Character constants

    # RFC 7230 §3.2.6: token = 1*tchar
    # tchar = "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
    _TCHAR_EXTRAS: ta.ClassVar[ta.FrozenSet[int]] = frozenset(b"!#$%&'*+-.^_`|~")

    _TCHAR: ta.ClassVar[ta.FrozenSet[int]] = frozenset(
        set(range(0x30, 0x3A)) |  # DIGIT 0-9
        set(range(0x41, 0x5B)) |  # ALPHA A-Z
        set(range(0x61, 0x7B)) |  # ALPHA a-z
        _TCHAR_EXTRAS,
    )

    # VCHAR = %x21-7E
    _VCHAR: ta.ClassVar[ta.FrozenSet[int]] = frozenset(range(0x21, 0x7F))

    # obs-text = %x80-FF
    _OBS_TEXT: ta.ClassVar[ta.FrozenSet[int]] = frozenset(range(0x80, 0x100))

    _SP = 0x20
    _HTAB = 0x09
    _CR = 0x0D
    _LF = 0x0A
    _COLON = 0x3A
    _NUL = 0x00

    # OWS = *( SP / HTAB )
    _OWS_CHARS: ta.ClassVar[ta.FrozenSet[int]] = frozenset({_SP, _HTAB})

    _CRLF = b'\r\n'
    _CRLFCRLF = b'\r\n\r\n'

    # Allowed characters as raw bytes for translate()
    _TCHAR_BYTES = bytes(sorted(_TCHAR))
    _VCHAR_BYTES = bytes(range(0x21, 0x7F))

    # Terminator verification

    def verify_terminator(self) -> None:
        data = self.data

        idx = data.find(self._CRLFCRLF)
        if idx >= 0:
            after = idx + 4
            if after < len(data):
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.TRAILING_DATA,
                    message=f'Unexpected {len(data) - after} byte(s) after header terminator',
                    line=0,
                    offset=after,
                )
            return

        # Bare-LF mode: require the header block to END with LF LF, not just contain it.
        if self.config.allow_bare_lf:
            if data.endswith(b'\n\n'):
                return
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
                message='Header block does not end with LFLF',
                line=0,
                offset=len(data),
            )

        raise HeaderFieldHttpParseError(
            code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
            message='Header block does not end with CRLFCRLF',
            line=0,
            offset=len(data),
        )

    # Line utilities

    def find_line_end(self, start: int) -> int:
        """
        Find the end of the current line (position of CR before CRLF, or LF if bare-LF allowed). Returns the index of
        the first byte of the line-ending sequence.

        Uses bytes.find() for NUL/CR/LF rather than iterating byte-by-byte in Python. Only loops when a bare CR must be
        skipped (allow_bare_cr_in_value mode).
        """

        data = self.data
        length = len(data)
        pos = start

        while True:
            # Let C-level .find() locate the first occurrence of each interesting byte.
            nul_at = data.find(b'\x00', pos)
            cr_at = data.find(b'\r', pos)
            lf_at = data.find(b'\n', pos)

            # Replace "not found" (-1) with length so min() picks the real hits.
            if nul_at < 0:
                nul_at = length
            if cr_at < 0:
                cr_at = length
            if lf_at < 0:
                lf_at = length

            first = min(nul_at, cr_at, lf_at)

            if first == length:
                # None of the three bytes found before end of data.
                break

            # NUL: always an error
            if first == nul_at and nul_at <= cr_at and nul_at <= lf_at:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                    message='NUL byte in header data',
                    line=self.current_line,
                    offset=nul_at,
                )

            # CR: check for CRLF vs bare CR
            if first == cr_at and cr_at <= lf_at:
                if cr_at + 1 < length and data[cr_at + 1] == self._LF:
                    return cr_at  # CRLF - this is the line ending

                # Bare CR (not followed by LF)
                if not self.config.allow_bare_cr_in_value:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.BARE_CARRIAGE_RETURN,
                        message='Bare CR not followed by LF',
                        line=self.current_line,
                        offset=cr_at,
                    )

                # Bare CR is allowed in values - skip past it and search again.
                pos = cr_at + 1
                continue

            # LF: bare LF (if it were preceded by CR we'd have returned above)
            if self.config.allow_bare_lf:
                return lf_at

            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.BARE_LF,
                message='Bare LF without preceding CR',
                line=self.current_line,
                offset=lf_at,
            )

        raise HeaderFieldHttpParseError(
            code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
            message='Unexpected end of data while scanning for line ending',
            line=self.current_line,
            offset=length,
        )

    def line_ending_len(self, line_end_pos: int) -> int:
        """Return the length of the line ending at *line_end_pos* (1 for LF, 2 for CRLF)."""

        if line_end_pos < len(self.data) and self.data[line_end_pos] == self._LF:
            return 1  # bare LF
        return 2  # CRLF

    # Kind detection

    def detect_kind(self, start_line: bytes) -> ParsedHttpMessage.Kind:
        if self.mode == HttpParser.Mode.REQUEST:
            return ParsedHttpMessage.Kind.REQUEST

        if self.mode == HttpParser.Mode.RESPONSE:
            return ParsedHttpMessage.Kind.RESPONSE

        # AUTO: responses start with "HTTP/"
        if start_line.startswith(b'HTTP/'):
            return ParsedHttpMessage.Kind.RESPONSE

        return ParsedHttpMessage.Kind.REQUEST

    # Start-line parsing

    _REQUEST_TARGET_BYTES: ta.ClassVar[bytes] = bytes(set(_VCHAR_BYTES) | set(range(0x80, 0x100)))

    def parse_request_line(self, line: bytes) -> ParsedHttpMessage.RequestLine:
        """Parse ``method SP request-target SP HTTP-version``."""

        # Must have exactly two SP separators

        first_sp = line.find(b' ')
        if first_sp < 0:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message='No SP found in request-line',
                line=0,
                offset=0,
            )

        last_sp = line.rfind(b' ')
        if first_sp == last_sp:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message='Only one SP found in request-line; expected method SP target SP version',
                line=0,
                offset=first_sp,
            )

        method_bytes = line[:first_sp]
        target_bytes = line[first_sp + 1:last_sp]
        version_bytes = line[last_sp + 1:]

        # Validate no extra SP in components: check that second SP search from first_sp+1 matches last_sp - i.e., the
        # target does not contain the last SP. Actually the HTTP spec says request-target can contain spaces? No - it's
        # defined as *visible ASCII*. But to find the correct split: method is a token (no SP), version is fixed format
        # (no SP), and everything in between is the target which is VCHAR (no SP). However, some real URIs... no, VCHAR
        # excludes SP. Let's be strict: Check there are exactly 2 SPs total.
        if line.count(b' ') != 2:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message=f'Request-line contains {line.count(b" ")} spaces; expected exactly 2',
                line=0,
                offset=0,
            )

        # Validate method

        if not method_bytes:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_METHOD,
                message='Empty method in request-line',
                line=0,
                offset=0,
            )

        if method_bytes.translate(None, self._TCHAR_BYTES):
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_METHOD,
                message=f'Method contains invalid character(s)',
                line=0,
                offset=0,
            )

        # Validate request-target (VCHAR only, non-empty)

        if not target_bytes:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                message='Empty request-target',
                line=0,
                offset=first_sp + 1,
            )

        if self.config.reject_non_visible_ascii_request_target:
            if target_bytes.translate(None, self._VCHAR_BYTES):
                raise StartLineHttpParseError(
                    code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                    message='Request-target contains non-visible-ASCII character(s)',
                    line=0,
                    offset=first_sp + 1,
                )

        else:
            if target_bytes.translate(None, self._REQUEST_TARGET_BYTES):
                raise StartLineHttpParseError(
                    code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                    message='Request-target contains invalid character(s)',
                    line=0,
                    offset=first_sp + 1,
                )

        # Validate HTTP version

        version_str = version_bytes.decode('ascii', errors='replace')
        if version_str == 'HTTP/1.0':
            version = HttpVersions.HTTP_1_0
        elif version_str == 'HTTP/1.1':
            version = HttpVersions.HTTP_1_1
        else:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.UNSUPPORTED_HTTP_VERSION,
                message=f'Unsupported HTTP version: {version_str!r}',
                line=0,
                offset=last_sp + 1,
            )

        return ParsedHttpMessage.RequestLine(
            method=method_bytes.decode('ascii'),
            request_target=target_bytes,
            http_version=version,
        )

    # reason-phrase: 0+ bytes of HTAB / SP / VCHAR / obs-text
    _RE_REASON_PHRASE: ta.ClassVar[re.Pattern] = re.compile(rb'^[\x09\x20\x21-\x7e\x80-\xff]*\Z')

    # reason-phrase = *( HTAB / SP / VCHAR / obs-text )
    _REASON_PHRASE_CHARS: ta.ClassVar[ta.FrozenSet[int]] = frozenset(
        {_HTAB, _SP} |
        set(_VCHAR) |
        set(_OBS_TEXT),
    )

    def parse_status_line(self, line: bytes) -> ParsedHttpMessage.StatusLine:
        """Parse ``HTTP-version SP status-code SP reason-phrase``."""

        # First SP separates version from status code

        first_sp = line.find(b' ')
        if first_sp < 0:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                message='No SP found in status-line',
                line=0,
                offset=0,
            )

        version_bytes = line[:first_sp]
        rest = line[first_sp + 1:]

        # Second SP separates status code from reason phrase

        second_sp = rest.find(b' ')
        if second_sp < 0:
            # Per RFC 7230:
            #   `status-line = HTTP-version SP status-code SP reason-phrase`.
            # The SP before reason-phrase is required even if reason-phrase is empty.
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                message='Missing second SP in status-line (required before reason-phrase)',
                line=0,
                offset=first_sp + 1 + len(rest),
            )

        status_bytes = rest[:second_sp]
        reason_bytes = rest[second_sp + 1:]

        # Validate HTTP version

        version_str = version_bytes.decode('ascii', errors='replace')
        if version_str == 'HTTP/1.0':
            version = HttpVersions.HTTP_1_0
        elif version_str == 'HTTP/1.1':
            version = HttpVersions.HTTP_1_1
        else:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.UNSUPPORTED_HTTP_VERSION,
                message=f'Unsupported HTTP version: {version_str!r}',
                line=0,
                offset=0,
            )

        # Validate status code: exactly 3 ASCII digits

        if len(status_bytes) != 3 or not status_bytes.isdigit():
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_STATUS_CODE,
                message=f'Status code is not exactly 3 digits: {status_bytes!r}',
                line=0,
                offset=first_sp + 1,
            )

        status_code = int(status_bytes)
        if not (100 <= status_code <= 599):
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_STATUS_CODE,
                message=f'Status code {status_code} out of range 100-599',
                line=0,
                offset=first_sp + 1,
            )

        # Validate reason-phrase characters

        if not self._RE_REASON_PHRASE.match(reason_bytes):
            # Regex rejected - scan to find the specific bad byte for error reporting
            reason_base_offset = first_sp + 1 + second_sp + 1

            for i, b in enumerate(reason_bytes):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in reason-phrase',
                        line=0,
                        offset=reason_base_offset + i,
                    )

                if b not in self._REASON_PHRASE_CHARS:
                    raise StartLineHttpParseError(
                        code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                        message=f'Invalid character 0x{b:02x} in reason-phrase',
                        line=0,
                        offset=reason_base_offset + i,
                    )

        return ParsedHttpMessage.StatusLine(
            http_version=version,
            status_code=status_code,
            reason_phrase=reason_bytes.decode('latin-1'),
        )

    # Header field parsing

    def parse_header_fields(self, start: int) -> ta.List[RawParsedHttpHeader]:
        """Parse all header fields from *start* until the empty-line terminator."""

        headers: ta.List[RawParsedHttpHeader] = []
        pos = start
        data = self.data
        self.current_line = 1  # line 0 is the start-line

        while pos < len(data):
            # Check for the empty line that terminates headers
            if data[pos] == self._CR and pos + 1 < len(data) and data[pos + 1] == self._LF:
                # Could be the terminator (\r\n at start of a "line" = empty line)
                break

            if self.config.allow_bare_lf and data[pos] == self._LF:
                break

            # Max header count check
            if len(headers) >= self.config.max_header_count:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.TOO_MANY_HEADERS,
                    message=f'Exceeded maximum header count of {self.config.max_header_count}',
                    line=self.current_line,
                    offset=pos,
                )

            # Find end of this header line
            line_end = self.find_line_end(pos)
            line_data = data[pos:line_end]
            next_pos = line_end + self.line_ending_len(line_end)

            if self.config.max_header_length is not None and len(line_data) > self.config.max_header_length:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                    message='Header line exceeds maximum length',
                    line=self.current_line,
                    offset=next_pos,
                )

            # Handle obs-fold: if the *next* line starts with SP or HTAB, it's a continuation
            obs_buf: ta.Optional[io.BytesIO] = None

            while next_pos < len(data):
                next_byte = data[next_pos]

                if next_byte in self._OWS_CHARS:
                    if not self.config.allow_obs_fold:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.OBS_FOLD_NOT_ALLOWED,
                            message='Obsolete line folding (obs-fold) encountered but not allowed',
                            line=self.current_line,
                            offset=next_pos,
                        )

                    # Unfold: find the end of the continuation line
                    cont_line_end = self.find_line_end(next_pos)
                    cont_data = data[next_pos:cont_line_end]

                    # Replace fold with single SP
                    if obs_buf is None:
                        obs_buf = io.BytesIO()
                        obs_buf.write(line_data)
                    obs_buf.write(b' ')
                    obs_buf.write(cont_data.lstrip(b' \t'))

                    next_pos = cont_line_end + self.line_ending_len(cont_line_end)

                    if self.config.max_header_length is not None and obs_buf.tell() > self.config.max_header_length:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                            message='Unfolded header line exceeds maximum length',
                            line=self.current_line,
                            offset=next_pos,
                        )

                else:
                    break

            if obs_buf is not None:
                line_data = obs_buf.getvalue()

            # Parse field-name : field-value
            header = self._parse_one_header(line_data, pos)
            headers.append(header)

            pos = next_pos
            self.current_line += 1

        return headers

    @classmethod
    def _strip_ows(cls, data: bytes) -> bytes:
        """Strip leading and trailing optional whitespace (SP / HTAB)."""

        return data.strip(b' \t')

    # token: 1+ tchar bytes
    _RE_TOKEN: ta.ClassVar[re.Pattern] = re.compile(rb"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+\Z")

    # Pre-calculate the 4 field-value variants for the translation filter (allow_bare_cr, reject_obs_text)
    _FIELD_VALUE_ALLOWED: ta.ClassVar[ta.Mapping[ta.Tuple[bool, bool], bytes]] = {
        (False, False): bytes({_HTAB, _SP}      | set(range(0x21, 0x7F))   | set(range(0x80, 0x100))),  # noqa
        (False, True):  bytes({_HTAB, _SP}      | set(range(0x21, 0x7F))),  # noqa
        (True, False):  bytes({_HTAB, _CR, _SP} | set(range(0x21, 0x7F))   | set(range(0x80, 0x100))),  # noqa
        (True, True):   bytes({_HTAB, _CR, _SP} | set(range(0x21, 0x7F))),  # noqa
    }

    def _parse_one_header(self, line_data: bytes, line_start_offset: int) -> RawParsedHttpHeader:
        """Parse a single ``field-name: field-value`` line (already unfolded)."""

        colon_idx = line_data.find(b':')
        if colon_idx < 0:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.MISSING_COLON,
                message='Header line has no colon separator',
                line=self.current_line,
                offset=line_start_offset,
            )

        name_bytes = line_data[:colon_idx]
        value_bytes = line_data[colon_idx + 1:]

        # Validate field-name

        if not name_bytes:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.EMPTY_FIELD_NAME,
                message='Empty field-name before colon',
                line=self.current_line,
                offset=line_start_offset,
            )

        # Check for space before colon
        if name_bytes[-1] in self._OWS_CHARS:
            if not self.config.allow_space_before_colon:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.SPACE_BEFORE_COLON,
                    message='Whitespace between field-name and colon',
                    line=self.current_line,
                    offset=line_start_offset + len(name_bytes) - 1,
                )

            # Strip trailing whitespace from name if allowed
            name_bytes = name_bytes.rstrip(b' \t')
            if not name_bytes:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.EMPTY_FIELD_NAME,
                    message='Field-name is only whitespace before colon',
                    line=self.current_line,
                    offset=line_start_offset,
                )

        # Validate name characters (regex fast-path; fallback scan on failure)
        if not self._RE_TOKEN.match(name_bytes):
            for i, b in enumerate(name_bytes):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

                if b >= 0x80:
                    raise EncodingHttpParseError(
                        code=EncodingHttpParseErrorCode.NON_ASCII_IN_FIELD_NAME,
                        message=f'Non-ASCII byte 0x{b:02x} in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

                if b not in self._TCHAR:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_NAME,
                        message=f'Invalid character 0x{b:02x} in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

        # Process field-value

        # Strip OWS
        value_stripped = self._strip_ows(value_bytes)

        # Check for empty value
        if not value_stripped and not self.config.allow_empty_header_values:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                message='Empty header field value not allowed',
                line=self.current_line,
                offset=line_start_offset + colon_idx + 1,
            )

        # Validate value characters (Translation fast-path)
        allowed_bytes = self._FIELD_VALUE_ALLOWED[(
            self.config.allow_bare_cr_in_value,
            self.config.reject_obs_text,
        )]

        # This is the "Pedantic" C-speed check. translate(None, allowed_bytes) removes all valid characters. If any
        # bytes remain, the input is invalid.
        invalid_chars = value_stripped.translate(None, allowed_bytes)

        if invalid_chars:
            value_base_offset = line_start_offset + colon_idx + 1
            # We only enter this Python loop if we ALREADY found an error.
            # This keeps the "happy path" fast while maintaining detailed error reporting.
            for i, b in enumerate(value_stripped):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in field-value',
                        line=self.current_line,
                        offset=value_base_offset + i,
                    )

                if b == self._CR:
                    if not self.config.allow_bare_cr_in_value:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.BARE_CARRIAGE_RETURN,
                            message='Bare CR in field-value',
                            line=self.current_line,
                            offset=value_base_offset + i,
                        )
                    continue

                if b not in allowed_bytes:
                    # Specific error logic for obs-text/bare CR
                    if b >= 0x80 and self.config.reject_obs_text:
                        raise EncodingHttpParseError(
                            code=EncodingHttpParseErrorCode.OBS_TEXT_IN_FIELD_VALUE,
                            message=f'obs-text byte 0x{b:02x} rejected by config',
                            line=self.current_line,
                            offset=value_base_offset + i,
                        )

                    # General character error
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                        message=f'Invalid character 0x{b:02x} in field-value',
                        line=self.current_line,
                        offset=value_base_offset + i,
                    )

        return RawParsedHttpHeader(
            name=name_bytes,
            value=value_stripped,
        )

    # Prepared header construction

    def prepare_headers(
        self,
        headers: ParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> PreparedParsedHttpHeaders:
        prepared = PreparedParsedHttpHeaders()

        self._prepare_content_length(headers, prepared)
        self._prepare_transfer_encoding(headers, prepared, kind, http_version)
        self._prepare_host(headers, prepared, kind, http_version)
        self._prepare_connection(headers, prepared, http_version)
        self._prepare_content_type(headers, prepared)
        self._prepare_te(headers, prepared)
        self._prepare_upgrade(headers, prepared)
        self._prepare_trailer(headers, prepared)
        self._prepare_expect(headers, prepared)
        self._prepare_date(headers, prepared)
        self._prepare_cache_control(headers, prepared)
        self._prepare_accept_encoding(headers, prepared)
        self._prepare_accept(headers, prepared)
        self._prepare_authorization(headers, prepared)

        # Cross-field: Content-Length + Transfer-Encoding conflict
        if (
            prepared.content_length is not None and
            prepared.transfer_encoding is not None and
            not self.config.allow_content_length_with_te
        ):
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.CONTENT_LENGTH_WITH_TRANSFER_ENCODING,
                message='Content-Length and Transfer-Encoding are both present',
            )

        return prepared

    def _prepare_content_length(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        values = headers.get_all('content-length')
        if not values:
            return

        parsed_values: ta.List[int] = []
        for v in values:
            # A single Content-Length header might itself be a comma-separated list (some implementations do this). We
            # parse each element.
            if self.config.reject_multi_value_content_length and ',' in v:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                    message=f'Content-Length with multiple values is forbidden: {v!r}',
                )

            for part in v.split(','):
                stripped = part.strip()

                if not stripped.isdigit():
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                        message=f'Content-Length value is not a valid non-negative integer: {stripped!r}',
                    )

                if (
                        self.config.max_content_length_str_len is not None and
                        len(stripped) > self.config.max_content_length_str_len
                ):
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                        message=f'Content-Length value string too long: {stripped!r}',
                    )

                parsed_values.append(int(stripped))

        if not parsed_values:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                message='Content-Length header present but empty',
            )

        unique = set(parsed_values)
        if len(unique) > 1:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.CONFLICTING_CONTENT_LENGTH,
                message=f'Conflicting Content-Length values: {sorted(unique)}',
            )

        if len(parsed_values) > 1:
            if not self.config.allow_multiple_content_lengths:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.DUPLICATE_CONTENT_LENGTH,
                    message=(
                        f'Multiple Content-Length values (all {parsed_values[0]}); '
                        f'set allow_multiple_content_lengths to accept'
                    ),
                )

        val = parsed_values[0]
        if val < 0:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                message=f'Content-Length is negative: {val}',
            )

        prepared.content_length = val

    _KNOWN_CODINGS: ta.ClassVar[ta.FrozenSet[str]] = frozenset([
        'chunked',
        'compress',
        'deflate',
        'gzip',
        'x-gzip',
        'x-compress',
    ])

    def _prepare_transfer_encoding(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> None:
        if 'transfer-encoding' not in headers:
            return

        combined = headers['transfer-encoding']
        codings = [c.strip().lower() for c in combined.split(',') if c.strip()]

        if not codings:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                message='Transfer-Encoding header present but empty',
            )

        # HTTP/1.0 check
        if http_version == HttpVersions.HTTP_1_0 and not self.config.allow_transfer_encoding_http10:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.TE_IN_HTTP10,
                message='Transfer-Encoding is not defined for HTTP/1.0',
            )

        # Validate known codings
        if not self.config.allow_unknown_transfer_encoding:
            for c in codings:
                if c not in self._KNOWN_CODINGS:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                        message=f'Unknown transfer-coding: {c!r}',
                    )

        # chunked positioning
        if 'chunked' in codings:
            if codings[-1] != 'chunked':
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                    message='chunked must be the last (outermost) transfer-coding',
                )

            if codings.count('chunked') > 1:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                    message='chunked appears more than once in Transfer-Encoding',
                )

        else:
            # No chunked present
            if kind == ParsedHttpMessage.Kind.REQUEST:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                    message='Transfer-Encoding in a request must include chunked as the last coding',
                )

            elif kind == ParsedHttpMessage.Kind.RESPONSE:
                if not self.config.allow_te_without_chunked_in_response:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                        message=(
                            'Transfer-Encoding in a response without chunked; '
                            'set allow_te_without_chunked_in_response to accept'
                        ),
                    )

        prepared.transfer_encoding = codings

    # Host header: reject control chars 0x00-0x1F and SP 0x20. # Operates on str (already latin-1 decoded).
    _RE_HOST_VALID: ta.ClassVar[re.Pattern] = re.compile(r'^[^\x00-\x20]*\Z')

    def _prepare_host(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> None:
        values = headers.get_all('host')

        if kind == ParsedHttpMessage.Kind.REQUEST and http_version == HttpVersions.HTTP_1_1:
            if not values and not self.config.allow_missing_host:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.MISSING_HOST_HEADER,
                    message='Host header is required in HTTP/1.1 requests',
                )

        if len(values) > 1:
            if not self.config.allow_multiple_hosts:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.MULTIPLE_HOST_HEADERS,
                    message=f'Multiple Host headers found ({len(values)})',
                )

            # If allowed, all values must be identical
            unique = set(values)
            if len(unique) > 1:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.CONFLICTING_HOST_HEADERS,
                    message=f'Multiple Host headers with different values: {sorted(unique)}',
                )

        if values:
            host_val = values[0].strip()

            # Minimal validation: reject any whitespace/control chars. Host is an authority, and
            # allowing OWS creates parsing inconsistencies across components.
            if not host_val and kind == ParsedHttpMessage.Kind.REQUEST:
                # Empty Host is technically allowed for certain request-targets (authority form, etc.), but let's just
                # accept it - the URI layer handles that.
                pass

            # Reject any SP / HTAB anywhere.
            if ' ' in host_val or '\t' in host_val:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_HOST,
                    message='Whitespace not allowed in Host header',
                )

            # Reject other C0 controls (including NUL) if present (defense in depth). (Host is a str decoded as Latin-1
            # in your ParsedHttpHeaders container.)
            if not self._RE_HOST_VALID.match(host_val):
                for i, ch in enumerate(host_val):
                    if ord(ch) < 0x21:  # includes 0x00-0x20; we've already rejected SP/HTAB explicitly
                        raise SemanticHeaderHttpParseError(
                            code=SemanticHeaderHttpParseErrorCode.INVALID_HOST,
                            message=f'Invalid character in Host header at position {i}',
                        )

            prepared.host = host_val

    @classmethod
    def _parse_comma_list(cls, value: str) -> ta.List[str]:
        """Split a comma-separated header value into trimmed, non-empty tokens."""

        parts: ta.List[str] = []
        for part in value.split(','):
            stripped = part.strip()
            if stripped:
                parts.append(stripped)
        return parts

    def _prepare_connection(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        http_version: HttpVersion,
    ) -> None:
        if 'connection' in headers:
            tokens = {t.lower() for t in self._parse_comma_list(headers['connection'])}
            prepared.connection = frozenset(tokens)
        else:
            prepared.connection = frozenset()

        # Derive keep_alive
        if 'close' in prepared.connection:
            prepared.keep_alive = False
        elif 'keep-alive' in prepared.connection:
            prepared.keep_alive = True
        else:
            # Default: HTTP/1.1 = keep-alive, HTTP/1.0 = close
            prepared.keep_alive = (http_version == HttpVersions.HTTP_1_1)

    @classmethod
    def _parse_quoted_string(cls, data: str, pos: int) -> ta.Tuple[str, int]:
        """
        Parse a quoted-string starting at *pos* (which must point at the opening DQUOTE). Returns (unescaped_value,
        position_after_closing_DQUOTE).
        """

        if pos >= len(data) or data[pos] != '"':
            raise ValueError('Expected opening double-quote')

        pos += 1  # skip opening "

        result: ta.List[str] = []
        while pos < len(data):
            ch = data[pos]

            if ch == '"':
                return ''.join(result), pos + 1

            if ch == '\\':
                pos += 1
                if pos >= len(data):
                    raise ValueError('Backslash at end of quoted-string')
                result.append(data[pos])
                pos += 1

            else:
                result.append(ch)
                pos += 1

        raise ValueError('Unterminated quoted-string')

    @classmethod
    def _parse_media_type_params(cls, params_str: str) -> ta.Dict[str, str]:
        """
        Parse ``;param=value`` segments from a Content-Type or Accept header. Values may be tokens or quoted-strings.
        """

        params: ta.Dict[str, str] = {}

        remaining = params_str.strip()
        while remaining:
            if not remaining.startswith(';'):
                break

            remaining = remaining[1:].strip()
            if not remaining:
                break

            eq_idx = remaining.find('=')
            if eq_idx < 0:
                # parameter name without value - skip to next semicolon or end
                semi_idx = remaining.find(';')
                if semi_idx < 0:
                    break

                remaining = remaining[semi_idx:]
                continue

            pname = remaining[:eq_idx].strip().lower()
            remaining = remaining[eq_idx + 1:].strip()

            if remaining.startswith('"'):
                try:
                    pvalue, end_pos = cls._parse_quoted_string(remaining, 0)
                except ValueError:
                    break
                remaining = remaining[end_pos:].strip()

            else:
                semi_idx = remaining.find(';')

                if semi_idx < 0:
                    pvalue = remaining.strip()
                    remaining = ''
                else:
                    pvalue = remaining[:semi_idx].strip()
                    remaining = remaining[semi_idx:]

            if pname:
                params[pname] = pvalue

        return params

    def _prepare_content_type(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'content-type' not in headers:
            return

        raw = headers['content-type']

        # media-type = type "/" subtype *( OWS ";" OWS parameter )
        semi_idx = raw.find(';')
        if semi_idx < 0:
            media_type = raw.strip().lower()
            params: ta.Dict[str, str] = {}
        else:
            media_type = raw[:semi_idx].strip().lower()
            params = self._parse_media_type_params(raw[semi_idx:])

        if '/' not in media_type:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_TYPE,
                message=f'Content-Type missing "/" in media-type: {media_type!r}',
            )

        parts = media_type.split('/', 1)
        if not parts[0] or not parts[1]:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_TYPE,
                message=f'Content-Type has empty type or subtype: {media_type!r}',
            )

        prepared.content_type = PreparedParsedHttpHeaders.ContentType(
            media_type=media_type,
            params=params,
        )

    @classmethod
    def _split_header_element(cls, element: str) -> ta.Tuple[str, float, ta.Dict[str, str]]:
        """
        Split a single header list element like ``"token;q=0.5;param=val"`` into ``(token_lower, q, params_dict)``.

        *token* is lowercased.  ``q`` defaults to ``1.0`` if absent.  The ``q`` key is consumed and **not** included in
        *params_dict*.  Raises ``ValueError`` on a malformed ``q`` value.
        """

        semi_idx = element.find(';')
        if semi_idx < 0:
            return element.strip().lower(), 1.0, {}

        token = element[:semi_idx].strip().lower()
        params = cls._parse_media_type_params(element[semi_idx:])

        q = 1.0
        q_str = params.pop('q', None)
        if q_str is not None:
            q = float(q_str)  # caller wraps ValueError

        return token, q, params

    def _prepare_te(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'te' not in headers:
            return

        codings = [
            self._split_header_element(p)[0]
            for p in self._parse_comma_list(headers['te'])
        ]

        prepared.te = [c for c in codings if c]

    def _prepare_upgrade(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'upgrade' not in headers:
            return

        prepared.upgrade = self._parse_comma_list(headers['upgrade'])

    # Headers that MUST NOT appear in trailers (RFC 7230 §4.1.2)
    _FORBIDDEN_TRAILER_FIELDS: ta.ClassVar[ta.FrozenSet[str]] = frozenset({
        'transfer-encoding',
        'content-length',
        'host',
        'cache-control',
        'expect',
        'max-forwards',
        'pragma',
        'range',
        'te',
        'authorization',
        'proxy-authenticate',
        'proxy-authorization',
        'www-authenticate',
        'content-encoding',
        'content-type',
        'content-range',
        'trailer',
    })

    def _prepare_trailer(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'trailer' not in headers:
            return

        fields = {f.lower() for f in self._parse_comma_list(headers['trailer'])}
        for f in fields:
            if f in self._FORBIDDEN_TRAILER_FIELDS:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.FORBIDDEN_TRAILER_FIELD,
                    message=f'Forbidden field in Trailer header: {f!r}',
                )

        prepared.trailer = frozenset(fields)

    def _prepare_expect(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'expect' not in headers:
            return

        raw = headers['expect'].strip().lower()
        if raw != '100-continue':
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_EXPECT,
                message=f'Only "100-continue" is accepted for Expect; got {raw!r}',
            )

        prepared.expect = raw
        prepared.expect_100_continue = True

    _MONTH_NAMES: ta.ClassVar[ta.Mapping[str, int]] = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12,
    }

    @classmethod
    def _parse_http_date(cls, value: str) -> datetime.datetime:
        """
        Parse an HTTP-date (RFC 7231 §7.1.1.1).

        Supports:
          - IMF-fixdate:  Sun, 06 Nov 1994 08:49:37 GMT
          - RFC 850:      Sunday, 06-Nov-94 08:49:37 GMT
          - asctime:      Sun Nov  6 08:49:37 1994
        """

        value = value.strip()

        # Try IMF-fixdate: day-name "," SP date1 SP time-of-day SP GMT
        # date1 = day SP month SP year (4-digit)
        if ',' in value:
            after_comma = value.split(',', 1)[1].strip()
            parts = after_comma.split()

            if len(parts) == 3 and parts[2].upper() == 'GMT' and '-' in parts[0]:
                # RFC 850: DD-Mon-YY HH:MM:SS GMT
                date_pieces = parts[0].split('-')
                if len(date_pieces) != 3:
                    raise ValueError(f'Invalid date component: {parts[0]}')

                day = int(date_pieces[0])
                month_str = date_pieces[1].lower()
                year_raw = int(date_pieces[2])

                # Two-digit year: RFC 7231 says interpret >= 50 as 19xx, < 50 as 20xx
                if year_raw < 100:
                    year = year_raw + 1900 if year_raw >= 50 else year_raw + 2000
                else:
                    year = year_raw

                time_pieces = parts[1].split(':')
                if len(time_pieces) != 3:
                    raise ValueError(f'Invalid time component: {parts[1]}')

                hour, minute, second = int(time_pieces[0]), int(time_pieces[1]), int(time_pieces[2])

                month = cls._MONTH_NAMES.get(month_str)
                if month is None:
                    raise ValueError(f'Invalid month: {month_str}')

                return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

            elif len(parts) == 5 and parts[4].upper() == 'GMT':
                # IMF-fixdate: DD Mon YYYY HH:MM:SS GMT
                day = int(parts[0])
                month_str = parts[1].lower()
                year = int(parts[2])

                time_pieces = parts[3].split(':')
                if len(time_pieces) != 3:
                    raise ValueError(f'Invalid time component: {parts[3]}')

                hour, minute, second = int(time_pieces[0]), int(time_pieces[1]), int(time_pieces[2])

                month = cls._MONTH_NAMES.get(month_str)
                if month is None:
                    raise ValueError(f'Invalid month: {month_str}')

                return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

            raise ValueError(f'Cannot parse date: {value}')

        else:
            # asctime: Sun Nov  6 08:49:37 1994 (Strict fixed-width check)
            # 012345678901234567890123
            # Sun Nov  6 08:49:37 1994
            if len(value) != 24:
                raise ValueError(f'Invalid asctime length: {len(value)}')

            month_str = value[4:7].lower()
            # Handle the space-padded day (e.g., " 6")
            day_str = value[8:10].replace(' ', '0')
            day = int(day_str)

            time_pieces = value[11:19].split(':')
            if len(time_pieces) != 3:
                raise ValueError('Invalid time component')
            hour, minute, second = map(int, time_pieces)

            year = int(value[20:24])
            month = cls._MONTH_NAMES.get(month_str)
            if month is None:
                raise ValueError(f'Invalid month: {month_str}')

            return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

    def _prepare_date(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'date' not in headers:
            return

        raw = headers['date']
        try:
            prepared.date = self._parse_http_date(raw)
        except (ValueError, IndexError, OverflowError) as e:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_DATE,
                message=f'Cannot parse Date header: {e}',
            ) from None

    def _prepare_cache_control(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'cache-control' not in headers:
            return

        directives: ta.Dict[str, ta.Optional[str]] = {}

        for part in self._parse_comma_list(headers['cache-control']):
            eq_idx = part.find('=')
            if eq_idx < 0:
                directives[part.lower()] = None
                continue

            name = part[:eq_idx].strip().lower()
            value = part[eq_idx + 1:].strip()
            if value.startswith('"'):
                try:
                    value, _ = self._parse_quoted_string(value, 0)
                except ValueError:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CACHE_CONTROL,
                        message=f'Invalid quoted-string in Cache-Control directive: {name}',
                    ) from None

            directives[name] = value

        prepared.cache_control = directives

    def _prepare_accept_encoding(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'accept-encoding' not in headers:
            return

        items: ta.List[PreparedParsedHttpHeaders.AcceptEncodingItem] = []

        for part in self._parse_comma_list(headers['accept-encoding']):
            try:
                coding, q, _ = self._split_header_element(part)
            except ValueError:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_ACCEPT_ENCODING,
                    message=f'Invalid q-value in Accept-Encoding: {part!r}',
                ) from None

            if coding:
                items.append(PreparedParsedHttpHeaders.AcceptEncodingItem(
                    coding=coding,
                    q=q,
                ))

        prepared.accept_encoding = items

    def _prepare_accept(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'accept' not in headers:
            return

        items: ta.List[PreparedParsedHttpHeaders.AcceptItem] = []

        for part in self._parse_comma_list(headers['accept']):
            try:
                media_range, q, params = self._split_header_element(part)
            except ValueError:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_ACCEPT,
                    message=f'Invalid q-value in Accept: {part!r}',
                ) from None

            items.append(PreparedParsedHttpHeaders.AcceptItem(
                media_range=media_range,
                q=q,
                params=params,
            ))

        prepared.accept = items

    def _prepare_authorization(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'authorization' not in headers:
            return

        raw = headers['authorization'].strip()
        if not raw:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_AUTHORIZATION,
                message='Authorization header is present but empty',
            )

        # scheme SP credentials (credentials may contain spaces for some schemes)
        sp_idx = raw.find(' ')
        if sp_idx < 0:
            # Scheme only, no credentials (e.g., some edge cases)
            prepared.authorization = PreparedParsedHttpHeaders.AuthorizationValue(
                scheme=raw,
                credentials='',
            )
        else:
            scheme = raw[:sp_idx]
            credentials = raw[sp_idx + 1:]
            prepared.authorization = PreparedParsedHttpHeaders.AuthorizationValue(
                scheme=scheme,
                credentials=credentials,
            )


##


def parse_http_message(
        data: bytes,
        mode: HttpParser.Mode = HttpParser.Mode.AUTO,
        config: ta.Optional[HttpParser.Config] = None,
) -> ParsedHttpMessage:
    parser = HttpParser(**(dict(config=config) if config is not None else {}))
    return parser.parse_message(data, mode=mode)


def parse_http_trailers(
        data: bytes,
        config: ta.Optional[HttpParser.Config] = None,
) -> ParsedHttpTrailers:
    parser = HttpParser(**(dict(config=config) if config is not None else {}))
    return parser.parse_trailers(data)


########################################
# ../../../../omlish/io/streams/types.py


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
    def write(self, data: BytesLikeOrMemoryview, /) -> None:
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
# ../../../../omlish/logs/infos.py
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
# ../../../../omlish/logs/metrics/base.py


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
# ../../../../omlish/logs/protocols.py


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
# ../core.py


##


class ChannelPipelineMessages(NamespaceClass):
    """Standard messages sent through a channel pipeline."""

    #

    class NeverInbound(Abstract):
        pass

    class NeverOutbound(Abstract):
        pass

    #

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

    #

    class Completable(Abstract, ta.Generic[T]):
        # Management of completable state is implemented as a 'hidden' / dynamic attributes to allow mixing in with
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

            cpl = ChannelPipelineMessages.Completable._Completion()  # noqa
            object.__setattr__(self, '_completion_', cpl)
            return cpl

        def add_listener(self, fn: ta.Callable[['ChannelPipelineMessages.Completable[T]'], None]) -> None:
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
            f'({self.handler!r})'  # {f"@{id(self.handler):x}"})'
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
            f'({self._handler!r})'  # @{id(self._handler):x})'
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
    def services(self) -> 'PipelineChannel.Services':  # noqa
        return self._pipeline._channel._services  # noqa

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

    #

    def _notify(self, no: ChannelPipelineHandlerNotification) -> None:
        check.isinstance(no, ChannelPipelineHandlerNotification)
        check.state(self._pipeline._channel._execution_depth > 0)  # noqa

        self._handler.notify(self, no)

    ##
    # Feeding `type`'s is forbidden as it's almost always going to be an error - usually forgetting to instantiate a
    # marker dataclass)

    _FORBIDDEN_INBOUND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        ChannelPipelineMessages.NeverInbound,
        ChannelPipelineHandlerNotification,
        type,
        type(None),
    )

    def _inbound(self, msg: ta.Any) -> None:
        if self._invalidated:
            raise ContextInvalidatedChannelPipelineError
        check.not_isinstance(msg, self._FORBIDDEN_INBOUND_TYPES)
        check.state(self._pipeline._channel._state == PipelineChannel.State.READY)  # noqa
        check.state(self._pipeline._channel._execution_depth > 0)  # noqa

        if isinstance(msg, ChannelPipelineMessages.MustPropagate):
            self._pipeline._channel._propagation.add_must(self, 'inbound', msg)  # noqa

        try:
            self._handler.inbound(self, msg)

        except self._pipeline._channel._all_never_handle_exceptions:  # type: ignore[misc]  # noqa
            raise

        except BaseException as e:
            if self._handling_error or self._pipeline._config.raise_immediately:  # noqa
                raise
            self._handle_error(e, 'inbound')

    _FORBIDDEN_OUTBOUND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        ChannelPipelineMessages.NeverOutbound,
        ChannelPipelineHandlerNotification,
        type,
        type(None),
    )

    def _outbound(self, msg: ta.Any) -> None:
        if self._invalidated:
            raise ContextInvalidatedChannelPipelineError
        check.not_isinstance(msg, self._FORBIDDEN_OUTBOUND_TYPES)
        check.state(self._pipeline._channel._state == PipelineChannel.State.READY)  # noqa
        check.state(self._pipeline._channel._execution_depth > 0)  # noqa

        if isinstance(msg, ChannelPipelineMessages.MustPropagate):
            self._pipeline._channel._propagation.add_must(self, 'outbound', msg)  # noqa

        try:
            self._handler.outbound(self, msg)

        except self._pipeline._channel._all_never_handle_exceptions:  # type: ignore[misc]  # noqa
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

            except self._pipeline._channel._all_never_handle_exceptions:  # type: ignore[misc]  # noqa
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
                ChannelPipelineMessages.NeverOutbound,
                ChannelPipelineHandlerNotification,
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

        #

        def update(self, **kwargs: ta.Any) -> 'ChannelPipeline.Config':
            return dc.replace(self, **kwargs)

        DEFAULT: ta.ClassVar['ChannelPipeline.Config']

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            *,
            _channel: 'PipelineChannel',
            _config: ta.Optional[Config] = None,
    ) -> None:
        super().__init__()

        self._channel: ta.Final[PipelineChannel] = _channel
        if _config is None:
            _config = ChannelPipeline.Config.DEFAULT
        self._config: ta.Final[ChannelPipeline.Config] = _config

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
        check.state(self._channel._state == PipelineChannel.State.READY)  # noqa

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
        self._channel._notify(ctx, ChannelPipelineHandlerNotifications.Added())  # noqa

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

        check.state(self._channel._state in (PipelineChannel.State.READY, PipelineChannel.State.DESTROYING))  # noqa

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
        self._channel._notify(ctx, ChannelPipelineHandlerNotifications.Removed())  # noqa

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

    @ta.final
    class _Outermost(ChannelPipelineHandler):
        """'Head' in Netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def outbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._propagation.remove_must(ctx, 'outbound', msg)  # noqa

            ctx._pipeline._channel._terminal_outbound(ctx, msg)  # noqa

    @ta.final
    class _Innermost(ChannelPipelineHandler):
        """'Tail' in Netty terms."""

        def __repr__(self) -> str:
            return f'{type(self).__name__}'

        def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                ctx._pipeline._channel._propagation.remove_must(ctx, 'inbound', msg)  # noqa

            ctx._pipeline._channel._terminal_inbound(ctx, msg)  # noqa

    #

    @ta.final
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


class PipelineChannelMetadata(Abstract):
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

        pipeline: ChannelPipeline.Config = ChannelPipeline.Config.DEFAULT

        def __post_init__(self) -> None:
            check.in_(self.inbound_terminal, ('drop', 'raise'))

        #

        DEFAULT: ta.ClassVar['PipelineChannel.Config']

        def update(self, **kwargs: ta.Any) -> 'PipelineChannel.Config':
            return dc.replace(self, **kwargs)

        def update_pipeline(self, **kwargs: ta.Any) -> 'PipelineChannel.Config':
            return self.update(pipeline=self.pipeline.update(**kwargs))

    Config.DEFAULT = Config()

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class Spec:
        # Initial handlers are optional - handlers may be freely added and removed later.
        handlers: ta.Sequence[ChannelPipelineHandler] = ()

        config: 'PipelineChannel.Config' = dc.field(default_factory=lambda: PipelineChannel.Config.DEFAULT)

        # _: dc.KW_ONLY

        metadata: ta.Union[ta.Sequence[PipelineChannelMetadata], 'PipelineChannel.Metadata'] = ()

        # Services are fixed for the lifetime of the channel.
        services: ta.Union[ta.Sequence[ChannelPipelineService], 'PipelineChannel.Services'] = ()

        #

        def update_config(self, **kwargs: ta.Any) -> 'PipelineChannel.Spec':
            return dc.replace(self, config=self.config.update(**kwargs))

        def update_pipeline_config(self, **kwargs: ta.Any) -> 'PipelineChannel.Spec':
            return dc.replace(self, config=self.config.update_pipeline(**kwargs))

    @classmethod
    def new(
            cls,
            handlers: ta.Sequence[ChannelPipelineHandler] = (),
            config: 'PipelineChannel.Config' = Config.DEFAULT,
            *,
            metadata: ta.Union[ta.Sequence[PipelineChannelMetadata], 'PipelineChannel.Metadata'] = (),
            services: ta.Union[ta.Sequence[ChannelPipelineService], 'PipelineChannel.Services'] = (),
    ) -> 'PipelineChannel':
        return cls(PipelineChannel.Spec(
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

        self._config: ta.Final[PipelineChannel.Config] = spec.config
        self._never_handle_exceptions = never_handle_exceptions

        self._metadata: ta.Final[PipelineChannel.Metadata] = PipelineChannel.Metadata.of(spec.metadata)
        self._services: ta.Final[PipelineChannel.Services] = PipelineChannel.Services.of(spec.services)

        self._output: ta.Final[PipelineChannel._Output] = PipelineChannel._Output()

        self._saw_final_input = False
        self._saw_final_output = False

        self._all_never_handle_exceptions: ta.Tuple[type, ...] = (
            UnhandleableChannelPipelineError,
            *never_handle_exceptions,
        )

        self._execution_depth = 0

        self._deferred: collections.deque[PipelineChannel._Deferred] = collections.deque()

        self._propagation: PipelineChannel._Propagation = PipelineChannel._Propagation(self)

        self._pipeline: ta.Final[ChannelPipeline] = ChannelPipeline(
            _channel=self,
            _config=spec.config.pipeline,
        )

        self._state = PipelineChannel.State.READY

        #

        try:
            for h in spec.handlers:
                self._pipeline.add_innermost(h)

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

    @property
    def pipeline(self) -> ChannelPipeline:
        return self._pipeline

    #

    class State(enum.Enum):
        NEW = 'new'
        READY = 'ready'
        DESTROYING = 'destroying'
        DESTROYED = 'destroyed'

    _state: State = State.NEW

    @property
    def state(self) -> State:
        return self._state

    #

    @property
    def saw_final_input(self) -> bool:
        return self._saw_final_input  # Note: only 'channel-level'

    @property
    def saw_final_output(self) -> bool:
        return self._saw_final_output

    #

    @ta.final
    class Metadata:
        def __init__(self, lst: ta.Sequence[PipelineChannelMetadata]) -> None:
            dct: ta.Dict[type, ta.Any] = {}
            for md in lst:
                ty = type(md)
                check.not_in(ty, dct)
                dct[ty] = md
            self._dct = dct

        @classmethod
        def of(cls, obj: ta.Union['PipelineChannel.Metadata', ta.Sequence[PipelineChannelMetadata]]) -> 'PipelineChannel.Metadata':  # noqa
            if isinstance(obj, cls):
                return obj
            else:
                return cls(list(obj))

        def __len__(self) -> int:
            return len(self._dct)

        def __contains__(self, ty: ta.Type[PipelineChannelMetadata]) -> bool:
            return ty in self._dct

        def __iter__(self) -> ta.Iterator[PipelineChannelMetadata]:
            return iter(self._dct.values())

        @dc.dataclass(frozen=True)
        class MetadataType(ta.Generic[PipelineChannelMetadataT]):
            """This is entirely just a workaround for mypy's `type-abstract` deficiency."""

            ty: ta.Type[PipelineChannelMetadataT]

        def __getitem__(
                self,
                ty: ta.Union[
                    MetadataType[PipelineChannelMetadataT],
                    ta.Type[PipelineChannelMetadataT],
                ],
        ) -> PipelineChannelMetadataT:
            if isinstance(ty, self.MetadataType):
                ty = ty.ty

            return self._dct[ty]

        @ta.overload
        def get(
                self,
                ty: ta.Union[
                    MetadataType[PipelineChannelMetadataT],
                    ta.Type[PipelineChannelMetadataT],
                ],
                default: PipelineChannelMetadataT,
                /,
        ) -> PipelineChannelMetadataT:
            ...

        @ta.overload
        def get(
                self,
                ty: ta.Union[
                    MetadataType[PipelineChannelMetadataT],
                    ta.Type[PipelineChannelMetadataT],
                ],
                default: ta.Optional[PipelineChannelMetadataT] = None,
                /,
        ) -> ta.Optional[PipelineChannelMetadataT]:
            ...

        def get(self, ty, default=None, /):
            if isinstance(ty, self.MetadataType):
                ty = ty.ty

            return self._dct.get(ty, default)

    @property
    def metadata(self) -> Metadata:
        return self._metadata

    #

    @ta.final
    class Services:
        def __init__(self, lst: ta.Sequence[ChannelPipelineService]) -> None:
            self._lst = lst

            self._by_type_cache: ta.Dict[type, ta.Sequence[ta.Any]] = {}
            self._single_by_type_cache: ta.Dict[type, ta.Optional[ta.Any]] = {}

            self._handles_handler_update: ta.Sequence[ChannelPipelineService] = [
                svc for svc in lst
                if type(svc).handler_update is not ChannelPipelineService.handler_update
            ]

        @classmethod
        def of(cls, obj: ta.Union['PipelineChannel.Services', ta.Sequence[ChannelPipelineService]]) -> 'PipelineChannel.Services':  # noqa
            if isinstance(obj, cls):
                return obj
            else:
                return cls(list(obj))

        def __len__(self) -> int:
            return len(self._lst)

        def __iter__(self) -> ta.Iterator[ChannelPipelineService]:
            return iter(self._lst)

        def __contains__(self, item: ChannelPipelineService) -> bool:
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
    def services(self) -> Services:
        return self._services

    #

    def _handler_update(self, ctx: ChannelPipelineHandlerContext, kind: ChannelPipelineHandlerUpdate) -> None:
        for svc in self._services._handles_handler_update:  # noqa
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

    @ta.final
    class _EnterContextManager:
        def __init__(self, ch: 'PipelineChannel') -> None:
            self._ch = ch

        def __enter__(self) -> None:
            self._ch._step_in()  # noqa

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            self._ch._step_out()  # noqa

    def enter(self) -> ta.ContextManager[None]:
        return self._EnterContextManager(self)

    #

    def _notify(self, ctx: ChannelPipelineHandlerContext, no: ChannelPipelineHandlerNotification) -> None:
        self._step_in()
        try:
            ctx._notify(no)  # noqa

        finally:
            self._step_out()

    def notify(self, handler_ref: ChannelPipelineHandlerRef, no: ChannelPipelineHandlerNotification) -> None:
        ctx = handler_ref._context  # noqa
        check.is_(ctx._pipeline, self._pipeline)  # noqa
        self._notify(ctx, no)

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

        self._output._q.append(msg)  # noqa

    #

    @ta.final
    class _Output:
        def __init__(self) -> None:
            self._q: ta.Final[collections.deque[ta.Any]] = collections.deque()

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

    #

    @ta.final
    class _Propagation:
        def __init__(self, ch: 'PipelineChannel') -> None:
            self._ch = ch

            if not self._ch._config.disable_propagation_checking:  # noqa
                self._pending_inbound_must: ta.Final[ta.Dict[int, ta.Tuple[ta.Any, ChannelPipelineHandlerContext]]] = {}
                self._pending_outbound_must: ta.Final[ta.Dict[int, ta.Tuple[ta.Any, ChannelPipelineHandlerContext]]] = {}  # noqa

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

    #

    def destroy(self) -> None:
        check.state(self._state == PipelineChannel.State.READY)
        self._state = PipelineChannel.State.DESTROYING

        self._step_in()
        try:
            im_ctx = self._pipeline._innermost  # noqa
            om_ctx = self._pipeline._outermost  # noqa
            while (ctx := im_ctx._next_out) is not om_ctx:  # noqa
                self._pipeline.remove(ctx._ref)  # noqa

        finally:
            self._step_out()

        self._state = PipelineChannel.State.DESTROYED


########################################
# ../../../../omlish/io/streams/base.py


##


class BaseByteStreamBufferLike(ByteStreamBufferLike, Abstract):
    def _norm_slice(self, start: int, end: ta.Optional[int]) -> ta.Tuple[int, int]:
        s, e, _ = slice(start, end, 1).indices(len(self))
        return (s, s) if e < s else (s, e)


########################################
# ../../../../omlish/io/streams/framing.py


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
# ../../../../omlish/io/streams/utils.py


##


class ByteStreamBuffers(NamespaceClass):
    @staticmethod
    def memoryview_to_bytes(mv: memoryview, /) -> bytes:
        if (((ot := type(obj := mv.obj)) is bytes or ot is bytearray or isinstance(obj, (bytes, bytearray))) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
            return obj  # type: ignore[return-value]

        return mv.tobytes()

    ##

    _CAN_CONVERT_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        bytes,
        bytearray,
        memoryview,
        ByteStreamBufferLike,
    )

    @classmethod
    def can_bytes(cls, obj: ta.Any, /) -> bool:
        return type(obj) in (cts := cls._CAN_CONVERT_TYPES) or isinstance(obj, cts)

    #

    @classmethod
    @ta.overload
    def buffer_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Optional[bytes]:
        ...

    @classmethod
    @ta.overload
    def buffer_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> bytes:
        ...

    @classmethod
    def buffer_to_bytes(cls, obj, or_none=False, /):
        if type(obj) is memoryview or isinstance(obj, memoryview):
            return cls.memoryview_to_bytes(obj)

        elif isinstance(obj, ByteStreamBufferView):
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
    def any_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Optional[bytes]:
        ...

    @classmethod
    @ta.overload
    def any_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> bytes:
        ...

    @classmethod
    def any_to_bytes(cls, obj, or_none=False, /):
        if (ot := type(obj)) is bytes:
            return obj
        elif ot is bytearray:
            return bytes(obj)

        elif isinstance(obj, bytes):
            return obj
        elif isinstance(obj, bytearray):
            return bytes(obj)

        else:
            return cls.buffer_to_bytes(obj, or_none)  # noqa

    #

    @classmethod
    @ta.overload
    def any_to_bytes_or_bytearray(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Union[bytes, bytearray, None]:
        ...

    @classmethod
    @ta.overload
    def any_to_bytes_or_bytearray(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> ta.Union[bytes, bytearray]:  # noqa
        ...

    @classmethod
    def any_to_bytes_or_bytearray(cls, obj, or_none=False, /):
        if (ot := type(obj)) is bytes or ot is bytearray or isinstance(obj, (bytes, bytearray)):
            return obj

        else:
            return cls.buffer_to_bytes(obj, or_none)  # noqa

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

    ##

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

    @staticmethod
    def split(buf: ByteStreamBuffer, sep: bytes, /, *, final: bool = False) -> ta.List[ByteStreamBufferView]:
        out: ta.List[ByteStreamBufferView] = []
        while (i := buf.find(sep)) >= 0:
            out.append(buf.split_to(i + 1))
        if final and len(buf):
            out.append(buf.split_to(len(buf)))
        return out


########################################
# ../../../../omlish/logs/contexts.py


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
# ../../../../omlish/logs/utils.py


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
# ../asyncs.py


##


class AsyncChannelPipelineMessages(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class Await(
        ChannelPipelineMessages.Completable[T],
        ChannelPipelineMessages.NeverInbound,
        ta.Generic[T],
    ):
        obj: ta.Awaitable[T]


########################################
# ../bytes/buffering.py


##


class InboundBytesBufferingChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    @abc.abstractmethod
    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        """Returning `None` denotes currently unknown/unanswerable."""

        raise NotImplementedError


########################################
# ../flow/types.py


##


class ChannelPipelineFlowMessages(NamespaceClass):
    """
    Note: these inbound messages will never be sent without a `ChannelPipelineFlow` instance in `channel.services` -
    thus it's safe to refer to `ctx.services[ChannelPipelineFlow]` when handling these.
    """

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushInput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelInboundInvoker::fireChannelReadComplete`  # noqa
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class PauseOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
        pass

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushOutput(ChannelPipelineMessages.NeverInbound):  # ~ Netty 'ChannelOutboundInvoker::flush'
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForInput(ChannelPipelineMessages.NeverInbound):  # ~ Netty `ChannelOutboundInvoker::read`
        pass


##


class ChannelPipelineFlow(ChannelPipelineService, Abstract):
    @abc.abstractmethod
    def is_auto_read(self) -> bool:
        raise NotImplementedError


########################################
# ../handlers/fns.py


##


class ChannelPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class NoContext(ta.Generic[F, T]):
        fn: ta.Callable[[F], T]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, obj: F) -> T:
            return self.fn(obj)

    @classmethod
    def no_context(cls, fn: ta.Callable[[F], T]) -> ChannelPipelineHandlerFn[F, T]:
        return cls.NoContext(fn)

    #

    @dc.dataclass(frozen=True)
    class And:
        fns: ta.Sequence[ChannelPipelineHandlerFn[ta.Any, bool]]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
            return all(fn(ctx, msg) for fn in self.fns)

    @classmethod
    def and_(cls, *fns: ChannelPipelineHandlerFn[ta.Any, bool]) -> ChannelPipelineHandlerFn[ta.Any, bool]:
        if len(fns) == 1:
            return fns[0]
        return cls.And(fns)

    #

    @dc.dataclass(frozen=True)
    class Or:
        fns: ta.Sequence[ChannelPipelineHandlerFn[ta.Any, bool]]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
            return any(fn(ctx, msg) for fn in self.fns)

    @classmethod
    def or_(cls, *fns: ChannelPipelineHandlerFn[ta.Any, bool]) -> ChannelPipelineHandlerFn[ta.Any, bool]:
        if len(fns) == 1:
            return fns[0]
        return cls.Or(fns)

    #

    @dc.dataclass(frozen=True)
    class Not:
        fn: ChannelPipelineHandlerFn[ta.Any, bool]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
            return not self.fn(ctx, msg)

    @classmethod
    def not_(cls, fn: ChannelPipelineHandlerFn[ta.Any, bool]) -> ChannelPipelineHandlerFn[ta.Any, bool]:
        if isinstance(fn, cls.Not):
            return fn.fn
        return cls.Not(fn)

    #

    @dc.dataclass(frozen=True)
    class IsInstance:
        ty: ta.Union[type, ta.Tuple[type, ...]]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.ty!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
            return isinstance(msg, self.ty)

    @classmethod
    def isinstance(cls, ty: ta.Union[type, ta.Tuple[type, ...]]) -> ChannelPipelineHandlerFn[ta.Any, bool]:
        return cls.IsInstance(ty)

    @classmethod
    def not_isinstance(cls, ty: ta.Union[type, ta.Tuple[type, ...]]) -> ChannelPipelineHandlerFn[ta.Any, bool]:
        return cls.Not(cls.IsInstance(ty))


##


class FnChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    @classmethod
    def of(
            cls,
            *,
            inbound: ta.Optional[ChannelPipelineHandlerFn[ta.Any, None]] = None,
            outbound: ta.Optional[ChannelPipelineHandlerFn[ta.Any, None]] = None,
    ) -> ChannelPipelineHandler:
        if inbound is not None and outbound is not None:
            return DuplexFnChannelPipelineHandler(inbound=inbound, outbound=outbound)
        elif inbound is not None:
            return InboundFnChannelPipelineHandler(inbound)
        elif outbound is not None:
            return OutboundFnChannelPipelineHandler(outbound)
        else:
            raise ValueError('At least one of inbound or outbound must be specified')


class InboundFnChannelPipelineHandler(FnChannelPipelineHandler):
    def __init__(self, inbound: ChannelPipelineHandlerFn[ta.Any, None]) -> None:
        super().__init__()

        self._inbound = inbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({self._inbound!r})'

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._inbound(ctx, msg)


class OutboundFnChannelPipelineHandler(FnChannelPipelineHandler):
    def __init__(self, outbound: ChannelPipelineHandlerFn[ta.Any, None]) -> None:
        super().__init__()

        self._outbound = outbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({self._outbound!r})'

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._outbound(ctx, msg)


class DuplexFnChannelPipelineHandler(FnChannelPipelineHandler):
    def __init__(
            self,
            *,
            inbound: ChannelPipelineHandlerFn[ta.Any, None],
            outbound: ChannelPipelineHandlerFn[ta.Any, None],
    ) -> None:
        super().__init__()

        self._inbound = inbound
        self._outbound = outbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}(inbound={self._inbound!r}, outbound={self._outbound!r})'

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._inbound(ctx, msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._outbound(ctx, msg)


########################################
# ../handlers/queues.py
"""
TODO:
 - max size, simple backpressure?
"""


##


class QueueChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    def __init__(
            self,
            *,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
            passthrough: ta.Union[bool, ta.Literal['must_propagate']] = 'must_propagate',
    ) -> None:
        super().__init__()

        self._filter = filter
        self._passthrough = passthrough

        self._q: collections.deque[ta.Any] = collections.deque()

    def __repr__(self) -> str:
        return ''.join([
            f'{type(self).__name__}@{id(self):x}',
            f'<len={len(self._q)}>',
            '(',
            ', '.join([
                *([f'filter={self._filter!r}'] if self._filter is not None else []),
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

    def _should_passthrough(self, msg: ta.Any) -> bool:
        if isinstance(pt := self._passthrough, bool):
            return pt

        elif pt == 'must_propagate':
            return isinstance(msg, ChannelPipelineMessages.MustPropagate)

        else:
            raise RuntimeError(f'Unknown passthrough mode {self._passthrough!r} for {self!r}')


class InboundQueueChannelPipelineHandler(QueueChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if (self._filter is not None and not self._filter(ctx, msg)):
            ctx.feed_in(msg)
            return

        self._append(msg)

        if self._should_passthrough(msg):
            ctx.feed_in(msg)


class OutboundQueueChannelPipelineHandler(QueueChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if (self._filter is not None and not self._filter(ctx, msg)):
            ctx.feed_out(msg)
            return

        self._append(msg)

        if self._should_passthrough(msg):
            ctx.feed_out(msg)


class DuplexQueueChannelPipelineHandler(
    InboundQueueChannelPipelineHandler,
    OutboundQueueChannelPipelineHandler,
):
    pass


########################################
# ../http/objects.py


##


class PipelineHttpMessageObject(Abstract):
    pass


class PipelineHttpMessageHead(PipelineHttpMessageObject, Abstract):
    @property
    @abc.abstractmethod
    def headers(self) -> HttpHeaders:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parsed(self) -> ta.Optional[ParsedHttpMessage]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> HttpVersion:
        raise NotImplementedError


class FullPipelineHttpMessage(PipelineHttpMessageObject, Abstract):
    @property
    @abc.abstractmethod
    def head(self) -> PipelineHttpMessageHead:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def body(self) -> BytesLikeOrMemoryview:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class PipelineHttpMessageContentChunkData(PipelineHttpMessageObject, Abstract):
    data: BytesLikeOrMemoryview


@dc.dataclass(frozen=True)
class PipelineHttpMessageEnd(PipelineHttpMessageObject, Abstract):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpMessageAborted(PipelineHttpMessageObject, Abstract):
    reason: str


##


def _un_abstract_pipeline_http_object_classes() -> None:
    # So this is regrettable, but I think the benefits of having the base objects be actual dataclasses outweighs the
    # gnarliness here.
    for cls in [PipelineHttpMessageHead, FullPipelineHttpMessage]:
        atts = {a for a in cls.__dict__ if not a.startswith('_')}
        for att in atts:
            delattr(cls, att)
        ams = check.isinstance(getattr(cls, '__abstractmethods__'), frozenset)
        setattr(cls, '__abstractmethods__', ams - atts)


_un_abstract_pipeline_http_object_classes()


########################################
# ../sched/types.py


##


class ChannelPipelineScheduling(ChannelPipelineService, Abstract):
    class Handle(Abstract):
        @abc.abstractmethod
        def cancel(self) -> None:
            raise NotImplementedError

    @abc.abstractmethod
    def schedule(
            self,
            handler_ref: ChannelPipelineHandlerRef,
            delay_s: float,
            fn: ta.Callable[[], None],
    ) -> Handle:
        raise NotImplementedError

    @abc.abstractmethod
    def cancel_all(self, handler_ref: ta.Optional[ChannelPipelineHandlerRef] = None) -> None:
        raise NotImplementedError


########################################
# ../../../../omlish/io/streams/direct.py


##


class BaseDirectByteStreamBufferLike(BaseByteStreamBufferLike, Abstract):
    def __init__(self, data: BytesLikeOrMemoryview) -> None:
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

    def __init__(self, data: BytesLikeOrMemoryview) -> None:
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
# ../../../../omlish/io/streams/scanning.py


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

    def write(self, data: BytesLikeOrMemoryview, /) -> None:
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
# ../../../../omlish/logs/base.py


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
# ../../../../omlish/logs/std/records.py
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
# ../bytes/queues.py


##


class InboundBytesBufferingQueueChannelPipelineHandler(
    InboundBytesBufferingChannelPipelineHandler,
    InboundQueueChannelPipelineHandler,
):
    def __init__(
            self,
            *,
            filter: ta.Union[ChannelPipelineHandlerFn[ta.Any, bool], ta.Literal[True], None] = None,  # noqa
            passthrough: bool = False,
    ) -> None:
        if filter is True:
            filter = ChannelPipelineHandlerFns.no_context(ByteStreamBuffers.can_bytes)  # noqa

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


FlatMapChannelPipelineHandlerFn = ChannelPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


class FlatMapChannelPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class Filter:
        pred: ChannelPipelineHandlerFn[ta.Any, bool]
        fn: FlatMapChannelPipelineHandlerFn
        else_fn: ta.Optional[FlatMapChannelPipelineHandlerFn] = None

        def __repr__(self) -> str:
            return (
                f'{type(self).__name__}('
                f'{self.pred!r}'
                f', {self.fn!r}'
                f'{f", else_fn={self.else_fn!r}" if self.else_fn is not None else ""}'
                f')'
            )

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.pred(ctx, msg):
                yield from self.fn(ctx, msg)
            elif (ef := self.else_fn) is not None:
                yield from ef(ctx, msg)  # noqa
            else:
                yield msg

    @classmethod
    def filter(
            cls,
            pred: ChannelPipelineHandlerFn[ta.Any, bool],
            fn: FlatMapChannelPipelineHandlerFn,
            else_fn: ta.Optional[FlatMapChannelPipelineHandlerFn] = None,
    ) -> FlatMapChannelPipelineHandlerFn:
        return cls.Filter(pred, fn, else_fn)

    #

    @dc.dataclass(frozen=True)
    class Concat:
        fns: ta.Sequence[FlatMapChannelPipelineHandlerFn]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            for fn in self.fns:
                yield from fn(ctx, msg)

    @classmethod
    def concat(cls, *fns: FlatMapChannelPipelineHandlerFn) -> FlatMapChannelPipelineHandlerFn:
        return cls.Concat(fns)

    #

    @dc.dataclass(frozen=True)
    class Compose:
        fns: ta.Sequence[FlatMapChannelPipelineHandlerFn]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        _fn: FlatMapChannelPipelineHandlerFn = dc.field(init=False)

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

            def compose(cur, nxt, ctx, msg):
                for x in cur(ctx, msg):
                    yield from nxt(ctx, x)

            xf: ta.Any = lambda ctx, msg: (msg,)  # noqa
            for cf in reversed(self.fns):
                xf = functools.partial(compose, cf, xf)

            object.__setattr__(self, '_fn', xf)

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return self._fn(ctx, msg)

    @classmethod
    def compose(cls, *fns: FlatMapChannelPipelineHandlerFn) -> FlatMapChannelPipelineHandlerFn:
        return cls.Compose(fns)

    #

    @dc.dataclass(frozen=True)
    class Map:
        fn: ChannelPipelineHandlerFn[ta.Any, ta.Any]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return (self.fn(ctx, msg),)

    @classmethod
    def map(cls, fn: ChannelPipelineHandlerFn[ta.Any, ta.Any]) -> FlatMapChannelPipelineHandlerFn:
        return cls.Map(fn)

    #

    @dc.dataclass(frozen=True)
    class Apply:
        fn: ChannelPipelineHandlerFn[ta.Any, None]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            self.fn(ctx, msg)
            return (msg,)

    @classmethod
    def apply(cls, fn: ChannelPipelineHandlerFn[ta.Any, None]) -> FlatMapChannelPipelineHandlerFn:
        return cls.Apply(fn)

    ##

    @dc.dataclass(frozen=True)
    class FeedOut:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            ctx.feed_out(msg)
            return (msg,)

    @classmethod
    def feed_out(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.FeedOut()

    #

    @dc.dataclass(frozen=True)
    class Drop:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return ()

    @classmethod
    def drop(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.Drop()


#


class FlatMapChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    def __init__(
            self,
            fn: FlatMapChannelPipelineHandlerFn,
    ) -> None:
        super().__init__()

        self._fn = check.callable(fn)

    _fn: FlatMapChannelPipelineHandlerFn

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._fn!r})'


#


class InboundFlatMapChannelPipelineHandler(FlatMapChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_in(x)


class OutboundFlatMapChannelPipelineHandler(FlatMapChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_out(x)


class DuplexFlatMapChannelPipelineHandler(
    InboundFlatMapChannelPipelineHandler,
    OutboundFlatMapChannelPipelineHandler,
):
    pass


#


class FlatMapChannelPipelineHandlers(NamespaceClass):
    _CLS_BY_DIRECTION: ta.ClassVar[ta.Mapping[ChannelPipelineDirectionOrDuplex, ta.Type[FlatMapChannelPipelineHandler]]] = {  # noqa
        'inbound': InboundFlatMapChannelPipelineHandler,
        'outbound': OutboundFlatMapChannelPipelineHandler,
        'duplex': DuplexFlatMapChannelPipelineHandler,
    }

    @classmethod
    def new(
            cls,
            direction: ChannelPipelineDirectionOrDuplex,
            fn: FlatMapChannelPipelineHandlerFn,
    ) -> ChannelPipelineHandler:
        h_cls = cls._CLS_BY_DIRECTION[direction]
        return h_cls(fn)

    #

    _NOT_MUST_PROPAGATE: ta.ClassVar[ChannelPipelineHandlerFn[ta.Any, bool]] = ChannelPipelineHandlerFns.not_(
        ChannelPipelineHandlerFns.isinstance(ChannelPipelineMessages.MustPropagate),
    )

    @classmethod
    def _add_drop_filters(
            cls,
            fn: FlatMapChannelPipelineHandlerFn,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> FlatMapChannelPipelineHandlerFn:
        if filter is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(filter, fn)

        if filter_type is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(
                ChannelPipelineHandlerFns.isinstance(filter_type),
                fn,
            )

        fn = FlatMapChannelPipelineHandlerFns.filter(cls._NOT_MUST_PROPAGATE, fn)

        return fn

    @classmethod
    def drop(
            cls,
            direction: ChannelPipelineDirectionOrDuplex,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> ChannelPipelineHandler:
        return cls.new(
            direction,
            cls._add_drop_filters(
                FlatMapChannelPipelineHandlerFns.drop(),
                filter=filter,
                filter_type=filter_type,
            ),
        )

    @classmethod
    def feed_out_and_drop(
            cls,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> ChannelPipelineHandler:
        return cls.new(
            'inbound',
            cls._add_drop_filters(
                FlatMapChannelPipelineHandlerFns.compose(
                    FlatMapChannelPipelineHandlerFns.feed_out(),
                    FlatMapChannelPipelineHandlerFns.drop(),
                ),
                filter=filter,
                filter_type=filter_type,
            ),
        )


########################################
# ../http/encoders.py


##


class PipelineHttpEncodingMessageAdapter(Abstract):
    @property
    def head_type(self) -> ta.Optional[ta.Type[PipelineHttpMessageHead]]:
        return None

    @property
    def full_type(self) -> ta.Optional[ta.Type[FullPipelineHttpMessage]]:
        return None

    @property
    def content_chunk_data_type(self) -> ta.Optional[ta.Type[PipelineHttpMessageContentChunkData]]:
        return None

    @property
    def end_type(self) -> ta.Optional[ta.Type[PipelineHttpMessageEnd]]:
        return None

    def encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        raise NotImplementedError


##


class PipelineHttpEncoder:
    def __init__(self, adapter: PipelineHttpEncodingMessageAdapter) -> None:
        super().__init__()

        self._adapter = adapter

        self._streaming = False
        self._chunked = False

    #

    def outbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        ty: ta.Any

        if (ty := self._adapter.head_type) is not None and isinstance(msg, ty):
            return self._handle_request_head(msg)

        elif (ty := self._adapter.content_chunk_data_type) is not None and isinstance(msg, ty):
            return self._handle_content_chunk_data(msg)

        elif (ty := self._adapter.end_type) is not None and isinstance(msg, ty):
            return self._handle_request_end(msg)

        elif (ty := self._adapter.full_type) is not None and isinstance(msg, ty):
            return self._handle_full_request(msg)

        else:
            return [msg]

    def _handle_request_head(self, msg: PipelineHttpMessageHead) -> ta.Sequence[ta.Any]:
        """Emit request line + headers, enter streaming mode."""

        self._streaming = True
        self._chunked = self._is_chunked(msg.headers)

        return [self._encode_head(msg)]

    def _handle_content_chunk_data(self, msg: PipelineHttpMessageContentChunkData) -> ta.Sequence[ta.Any]:
        """Emit body chunk (raw or chunked-encoded)."""

        if not self._streaming:
            # Not in streaming mode - pass through unchanged
            return [msg]

        elif len(msg.data) < 1:
            return []

        elif self._chunked:
            # Chunked encoding: <size-hex>\r\n<data>\r\n
            return [
                f'{len(msg.data):x}\r\n'.encode('ascii'),
                msg.data,
                b'\r\n',
            ]

        else:
            # Raw data
            return [msg.data]

    def _handle_request_end(self, msg: PipelineHttpMessageEnd) -> ta.Sequence[ta.Any]:
        """Emit terminator if chunked, reset state."""

        if not self._streaming:
            # Not in streaming mode - pass through
            return [msg]

        was_chunked = self._chunked

        # Reset state
        self._streaming = False
        self._chunked = False

        if was_chunked:
            # Emit final chunk: 0\r\n\r\n
            return [b'0\r\n\r\n']
        else:
            return []

    def _handle_full_request(self, msg: FullPipelineHttpMessage) -> ta.Any:
        """Emit complete request in one shot."""

        return [
            self._encode_head(msg.head),
            *([msg.body] if len(msg.body) > 0 else []),
        ]

    #

    def _encode_head(self, head: PipelineHttpMessageHead) -> bytes:
        buf = io.BytesIO()

        buf.write(self._adapter.encode_head_line(head))

        for hl in self._encode_headers(head.headers):
            buf.write(hl)

        buf.write(b'\r\n')

        return buf.getvalue()

    def _encode_headers(self, headers: HttpHeaders) -> ta.List[bytes]:
        """Encode headers as 'Name: value\r\n' lines."""

        lines: ta.List[bytes] = []

        # HttpHeaders stores entries as list of (name, value) tuples
        for name, value in headers.raw:
            # Header names and values should be ASCII-safe in practice
            line = f'{name}: {value}\r\n'.encode('ascii')
            lines.append(line)

        return lines

    def _is_chunked(self, headers: HttpHeaders) -> bool:
        """Check if Transfer-Encoding includes 'chunked'."""

        te = headers.lower.get('transfer-encoding', ())
        return 'chunked' in te


########################################
# ../http/requests.py


##


class PipelineHttpRequestObject(PipelineHttpMessageObject, Abstract):
    pass


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class PipelineHttpRequestHead(PipelineHttpMessageHead, PipelineHttpRequestObject):
    method: str
    target: str

    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None

    version: HttpVersion = HttpVersions.HTTP_1_1


@dc.dataclass(frozen=True)
class FullPipelineHttpRequest(FullPipelineHttpMessage, PipelineHttpRequestObject):
    head: PipelineHttpRequestHead
    body: BytesLikeOrMemoryview

    @classmethod
    def simple(
            cls,
            host: str,
            target: str,
            *,
            method: str = 'GET',
            version: HttpVersion = HttpVersions.HTTP_1_1,

            content_type: ta.Optional[str] = None,
            body: bytes = b'',
            connection: str = 'close',

            headers: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> 'FullPipelineHttpRequest':
        return cls(
            head=PipelineHttpRequestHead(
                method=method,
                target=target,
                version=version,
                headers=HttpHeaders([
                    ('Host', host),
                    *([('Content-Type', content_type)] if content_type is not None else []),
                    *([('Content-Length', str(len(body)))] if body else []),
                    ('Connection', connection),
                    *(headers.items() if headers else []),
                ]),
            ),
            body=body,
        )


@dc.dataclass(frozen=True)
class PipelineHttpRequestContentChunkData(PipelineHttpMessageContentChunkData, PipelineHttpRequestObject):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpRequestEnd(PipelineHttpMessageEnd, PipelineHttpRequestObject):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpRequestAborted(PipelineHttpMessageAborted, PipelineHttpRequestObject):
    pass


########################################
# ../http/responses.py


##


class PipelineHttpResponseObject(PipelineHttpMessageObject, Abstract):
    pass


@install_dataclass_kw_only_init()
@dc.dataclass(frozen=True)
class PipelineHttpResponseHead(PipelineHttpMessageHead, PipelineHttpResponseObject):
    status: int
    reason: str

    headers: HttpHeaders
    parsed: ta.Optional[ParsedHttpMessage] = None

    version: HttpVersion = HttpVersions.HTTP_1_1

    @staticmethod
    def get_reason_phrase(code: int) -> str:
        try:
            return http.HTTPStatus(code).phrase
        except ValueError:
            return ''


@dc.dataclass(frozen=True)
class FullPipelineHttpResponse(FullPipelineHttpMessage, PipelineHttpResponseObject):
    head: PipelineHttpResponseHead
    body: BytesLikeOrMemoryview

    @classmethod
    def simple(
            cls,
            *,
            version: HttpVersion = HttpVersions.HTTP_1_1,
            status: int = 200,
            reason: ta.Optional[str] = None,

            content_type: str = 'text/plain; charset=utf-8',
            body: bytes = b'',
            connection: str = 'close',

            headers: ta.Optional[ta.Mapping[str, str]] = None,
    ):
        return cls(
            head=PipelineHttpResponseHead(
                version=version,
                status=status,
                reason=PipelineHttpResponseHead.get_reason_phrase(status) if reason is None else reason,
                headers=HttpHeaders([
                    ('Content-Type', content_type),
                    ('Content-Length', str(len(body))),
                    ('Connection', connection),
                    *(headers.items() if headers else []),
                ]),
            ),
            body=body,
        )


@dc.dataclass(frozen=True)
class PipelineHttpResponseContentChunkData(PipelineHttpMessageContentChunkData, PipelineHttpResponseObject):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpResponseEnd(PipelineHttpMessageEnd, PipelineHttpResponseObject):
    pass


@dc.dataclass(frozen=True)
class PipelineHttpResponseAborted(PipelineHttpMessageAborted, PipelineHttpResponseObject):
    pass


########################################
# ../../../../omlish/io/streams/segmented.py


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
            self._len += len(mv)

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
            return bytes(self._segs[0])
        return b''.join(bytes(mv) for mv in self._segs)


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
            self._segs[-1] = bytes(memoryview(a)[:used])

        else:
            # Try to shrink in-place to used bytes. If exported views exist, this can BufferError; fall back to bytes()
            # in that case.
            if not self._segs or self._segs[-1] is not a:
                raise RuntimeError('active not at tail')
            try:
                del a[used:]  # may raise BufferError if any exports exist
            except BufferError:
                self._segs[-1] = bytes(memoryview(a)[:used])

        self._active = None
        self._active_used = 0

    def write(self, data: BytesLikeOrMemoryview, /) -> None:
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
            bb = bytes(memoryview(b)[:n])
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
# ../../../../omlish/logs/asyncs.py


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
# ../../../../omlish/logs/std/loggers.py


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
# ../http/client/requests.py


##


class RequestPipelineHttpEncodingMessageAdapter(PipelineHttpEncodingMessageAdapter):
    head_type: ta.Final[ta.Type[PipelineHttpMessageHead]] = PipelineHttpRequestHead
    full_type: ta.Final[ta.Type[FullPipelineHttpMessage]] = FullPipelineHttpRequest
    content_chunk_data_type: ta.Final[ta.Type[PipelineHttpMessageContentChunkData]] = PipelineHttpRequestContentChunkData  # noqa
    end_type: ta.Final[ta.Type[PipelineHttpMessageEnd]] = PipelineHttpRequestEnd

    def encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpRequestHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{head.method} {head.target} {version_str}\r\n'.encode('ascii')


##


class PipelineHttpRequestEncoder(ChannelPipelineHandler):
    def __init__(self) -> None:
        super().__init__()

        self._encoder = PipelineHttpEncoder(
            RequestPipelineHttpEncodingMessageAdapter(),
        )

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, PipelineHttpRequestObject):
            ctx.feed_out(msg)
            return

        for out_msg in self._encoder.outbound(msg):
            ctx.feed_out(out_msg)


########################################
# ../http/server/responses.py


##


class ResponsePipelineHttpEncodingMessageAdapter(PipelineHttpEncodingMessageAdapter):
    head_type: ta.Final[ta.Type[PipelineHttpMessageHead]] = PipelineHttpResponseHead
    full_type: ta.Final[ta.Type[FullPipelineHttpMessage]] = FullPipelineHttpResponse
    content_chunk_data_type: ta.Final[ta.Type[PipelineHttpMessageContentChunkData]] = PipelineHttpResponseContentChunkData  # noqa
    end_type: ta.Final[ta.Type[PipelineHttpMessageEnd]] = PipelineHttpResponseEnd

    def encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpResponseHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{version_str} {head.status} {head.reason}\r\n'.encode('ascii')


##


class PipelineHttpResponseEncoder(ChannelPipelineHandler):
    def __init__(self) -> None:
        super().__init__()

        self._encoder = PipelineHttpEncoder(
            ResponsePipelineHttpEncodingMessageAdapter(),
        )

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, PipelineHttpResponseObject):
            ctx.feed_out(msg)
            return

        for out_msg in self._encoder.outbound(msg):
            ctx.feed_out(out_msg)


########################################
# ../../../../omlish/logs/modules.py


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
# ../bytes/decoders.py
"""
TODO:
 - netty 'pending_removal' trick
"""


##


class UnicodeDecoderChannelPipelineHandler(ChannelPipelineHandler):
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

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if ByteStreamBuffers.can_bytes(msg):
            b = ByteStreamBuffers.any_to_bytes(msg)

            msg = b.decode(self._encoding, errors=self._errors)

        ctx.feed_in(msg)


##


class DelimiterFrameDecoderChannelPipelineHandler(InboundBytesBufferingChannelPipelineHandler):
    """
    bytes-like -> frames using longest-match delimiter semantics.

    TODO:
     - flow control, *or* replace with BytesToMessageDecoderChannelPipelineHandler
    """

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
            max_buffer: ta.Optional[int] = None,
            buffer_chunk_size: int = 0x10000,
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

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
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

    def _produce_frames(self, ctx: ChannelPipelineHandlerContext, *, final: bool = False) -> None:
        frames = self._fr.decode(self._buf, final=final)

        if final and len(self._buf):
            if (oif := self._on_incomplete_final) == 'allow':
                frames.append(self._buf.split_to(len(self._buf)))
            elif oif == 'raise':
                raise IncompleteDecodingChannelPipelineError
            else:
                raise RuntimeError(f'unexpected on_incomplete_final: {oif!r}')

        for fr in frames:
            ctx.feed_in(fr)


##


class BytesToMessageDecoderChannelPipelineHandler(InboundBytesBufferingChannelPipelineHandler, Abstract):
    def __init__(
            self,
            *,
            max_buffer_size: ta.Optional[int] = None,
            buffer_chunk_size: int = 0x10000,
            scanning_buffer: bool = False,
    ) -> None:
        super().__init__()

        self._max_buffer_size = max_buffer_size
        self._buffer_chunk_size = buffer_chunk_size
        self._scanning_buffer = scanning_buffer

    def inbound_buffered_bytes(self) -> int:
        if (buf := self._buf) is None:
            return 0
        return len(buf)

    @abc.abstractmethod
    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> ta.Iterable[ta.Any]:
        raise NotImplementedError

    #

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

    _called_decode: bool = False  # ~ `selfFiredChannelRead`
    _produced_messages: bool = False  # ~ `firedChannelRead`

    def _call_decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> None:
        self._called_decode = True

        try:
            out = list(self._decode(ctx, buf, final=final))
        except DecodingChannelPipelineError:
            raise
        except Exception as e:
            raise DecodingChannelPipelineError from e

        if not out:
            return

        self._produced_messages = True

        for out_msg in out:
            ctx.feed_in(out_msg)

    #

    def _on_flush_input(self, ctx: ChannelPipelineHandlerContext) -> None:
        if (
                self._called_decode and
                not self._produced_messages and
                not ctx.services[ChannelPipelineFlow].is_auto_read()
        ):
            ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

        self._called_decode = False
        self._produced_messages = False

        ctx.feed_in(ChannelPipelineFlowMessages.FlushInput())

    def _on_final_input(self, ctx: ChannelPipelineHandlerContext, msg: ChannelPipelineMessages.FinalInput) -> None:
        dec_buf: ByteStreamBuffer
        if self._buf is not None:
            dec_buf = self._buf
        else:
            dec_buf = DirectByteStreamBuffer(b'')

        self._call_decode(ctx, dec_buf, final=True)

        ctx.feed_in(msg)

    def _on_bytes_input(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        check.arg(len(msg) > 0)

        if self._buf is None:
            self._buf = self._new_buf()

        for seg in ByteStreamBuffers.iter_segments(msg):
            self._buf.write(seg)

        self._call_decode(ctx, self._buf)

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            self._on_flush_input(ctx)

        elif isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._on_final_input(ctx, msg)

        elif ByteStreamBuffers.can_bytes(msg):
            self._on_bytes_input(ctx, msg)

        else:
            ctx.feed_in(msg)


#


@ta.final
class FnBytesToMessageDecoderChannelPipelineHandler(BytesToMessageDecoderChannelPipelineHandler):
    class DecodeFn(ta.Protocol):
        def __call__(
                self,
                ctx: ChannelPipelineHandlerContext,
                buf: ByteStreamBuffer,
                *,
                final: bool = False,
        ) -> ta.Iterable[ta.Any]:
            ...

    def __init__(
            self,
            decode_fn: DecodeFn,
            *,
            max_buffer_size: ta.Optional[int] = None,
            buffer_chunk_size: int = 0x10000,
            scanning_buffer: bool = False,
    ) -> None:
        super().__init__(
            max_buffer_size=max_buffer_size,
            buffer_chunk_size=buffer_chunk_size,
            scanning_buffer=scanning_buffer,
        )

        self._decode_fn = decode_fn

    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> ta.Iterable[ta.Any]:
        return self._decode_fn(ctx, buf, final=final)


########################################
# ../http/decoders.py
"""
TODO:
 - chunked make_chunk_header - https://datatracker.ietf.org/doc/html/rfc9112#name-chunk-extensions
  - and make_content_chunk_data ...
 - fix exception handling lol - do we raise ValueError?? do we return aborted??
 - unify with pipelines.bytes.decoders
"""


##


@dc.dataclass(frozen=True)
class PipelineHttpDecodingConfig:
    DEFAULT: ta.ClassVar['PipelineHttpDecodingConfig']

    parser_config: ta.Optional[HttpParser.Config] = None

    @dc.dataclass(frozen=True)
    class BufferConfig:
        max_size: ta.Optional[int]
        chunk_size: int

    head_buffer: BufferConfig = BufferConfig(max_size=0x1000, chunk_size=0x1000)

    max_content_chunk_size: ta.Optional[int] = None
    content_chunk_header_buffer: BufferConfig = BufferConfig(max_size=1024, chunk_size=1024)

    aggregated_body_buffer: BufferConfig = BufferConfig(max_size=0x10000, chunk_size=0x10000)


PipelineHttpDecodingConfig.DEFAULT = PipelineHttpDecodingConfig()


##


class PipelineHttpDecodingMessageAdapter(Abstract):
    def make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        raise NotImplementedError

    def make_aborted(self, reason: str) -> ta.Any:
        raise NotImplementedError

    def make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        raise NotImplementedError

    def make_end(self) -> ta.Any:
        raise NotImplementedError


##


class PipelineHttpHeadDecoder:
    """
    Class for HTTP/1.x head decoders (request or response).

    Handles common logic:
      - Buffering until b'\\r\\n\\r\\n'
      - Parsing request/response line + headers
      - Forwarding remainder bytes
      - EOF handling
    """

    def __init__(
            self,
            adapter: PipelineHttpDecodingMessageAdapter,
            parse_mode: HttpParser.Mode,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._adapter = adapter
        self._parse_mode = parse_mode
        self._config = config

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_size=config.head_buffer.max_size,
            chunk_size=config.head_buffer.chunk_size,
        ))

    _done = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound_buffered_bytes(self) -> int:
        if self._done:
            return 0
        return len(self._buf)

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            # EOF: if we have partial head buffered and haven't parsed head, that's an error.

            del self._buf
            self._done = True

            return [
                self._adapter.make_aborted('EOF before HTTP head complete'),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._done:
                out.append(mv)
                continue

            rem_mv: ta.Optional[memoryview] = None

            if (max_buf := self._buf.max_size) is not None:
                rem_buf = max_buf - len(self._buf)

                if len(mv) > rem_buf:
                    self._buf.write(mv[:rem_buf])
                    rem_mv = mv[rem_buf:]
                else:
                    self._buf.write(mv)

            # Look for end of head
            i = self._buf.find(b'\r\n\r\n')
            if i < 0:
                if rem_mv is not None:
                    del self._buf
                    self._done = True

                    return [self._adapter.make_aborted('Head exceeded max buffer size')]

                continue

            # Extract head
            head_view = self._buf.split_to(i + 4)

            # Parse and emit head
            raw = head_view.tobytes()
            parsed = parse_http_message(
                raw,
                mode=self._parse_mode,
                config=self._config.parser_config,
            )

            head = self._adapter.make_head(parsed)
            out.append(head)

            # Forward any remainder bytes (body bytes)
            if len(self._buf):
                rem_view = self._buf.split_to(len(self._buf))
                out.append(rem_view)

            if rem_mv is not None:
                out.append(rem_mv)

            del self._buf
            self._done = True

        return out


##


class PipelineHttpContentChunkDecoder(Abstract):
    def __init__(
            self,
            adapter: PipelineHttpDecodingMessageAdapter,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._adapter = adapter
        self._config = config

    @property
    @abc.abstractmethod
    def done(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound_buffered_bytes(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        raise NotImplementedError


class UntilFinalInputPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    _done: bool = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound_buffered_bytes(self) -> int:
        return 0

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._done = True

            return [
                self._adapter.make_end(),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            out.append(self._adapter.make_content_chunk_data(mv))

        return out


class ContentLengthPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    def __init__(
            self,
            adapter: PipelineHttpDecodingMessageAdapter,
            content_length: int,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        check.arg(content_length > 0)

        super().__init__(
            adapter,
            config=config,
        )

        self._remain = content_length

    @property
    def done(self) -> bool:
        return self._remain < 1

    def inbound_buffered_bytes(self) -> int:
        return 0

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(self._remain > 0)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._remain = 0

            return [
                self._adapter.make_aborted('EOF before HTTP body complete'),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._remain < 1:
                out.append(mv)
                continue

            mvl = len(mv)

            if self._remain > mvl:
                out.append(self._adapter.make_content_chunk_data(mv))
                self._remain -= mvl

            elif self._remain == mvl:
                out.append(self._adapter.make_content_chunk_data(mv))
                out.append(self._adapter.make_end())
                self._remain = 0

            else:
                out.append(self._adapter.make_content_chunk_data(mv[:self._remain]))
                out.append(self._adapter.make_end())
                ofs = self._remain
                self._remain = 0
                out.append(mv[ofs:])

        return out


class ChunkedPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    """
    Class for HTTP/1.x chunked transfer encoding decoders.

    Handles common logic:
      - Parsing hex chunk sizes
      - Extracting chunk data
      - Validating CRLF delimiters
      - Detecting terminator (0\\r\\n\\r\\n)
      - State machine: 'size' -> 'data' -> 'size' ... -> 'trailer' -> 'done'
    """

    def __init__(
            self,
            adapter: PipelineHttpDecodingMessageAdapter,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__(
            adapter,
            config=config,
        )

        self._header_buf = self._new_header_buf()

        self._chunk_remaining = 0
        self._got_cr = False

        self._state: ta.Literal['size', 'data', 'trailer', 'done'] = 'size'

    def _new_header_buf(self) -> MutableByteStreamBuffer:
        return ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_size=self._config.content_chunk_header_buffer.max_size,
            chunk_size=self._config.content_chunk_header_buffer.chunk_size,
        ))

    @property
    def done(self) -> bool:
        return self._state == 'done'

    def inbound_buffered_bytes(self) -> int:
        if self._state == 'done':
            return 0
        return len(self._header_buf)

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(self._state != 'done')

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            del self._header_buf
            self._state = 'done'

            return [
                self._adapter.make_aborted('EOF before chunked encoding complete'),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            if not self._process(mv, out):
                break

        return out

    def _process(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        if self._state == 'done':
            out.append(mv)
            return True

        elif self._state == 'size':
            return self._process_size(mv, out)

        elif self._state == 'data':
            return self._process_data(mv, out)

        elif self._state == 'trailer':
            return self._process_trailer(mv, out)

        else:
            raise RuntimeError(f'Invalid state: {self._state!r}')

    def _process_size(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        rem_mv: ta.Optional[memoryview] = None

        if (max_buf := self._header_buf.max_size) is not None:
            rem_buf = max_buf - len(self._header_buf)

            if len(mv) > rem_buf:
                self._header_buf.write(mv[:rem_buf])
                rem_mv = mv[rem_buf:]
            else:
                self._header_buf.write(mv)

        # Parse chunk size line: <hex-size>\r\n
        i = self._header_buf.find(b'\r\n')
        if i < 0:
            if rem_mv is not None:
                del self._header_buf
                self._state = 'done'

                out.append(self._adapter.make_aborted('Chunk header exceeded max buffer size'))
                return False

            return True  # Need more data

        size_line = self._header_buf.split_to(i + 2)

        size_bytes = size_line.tobytes()[:-2]  # Strip \r\n
        try:
            self._chunk_remaining = int(size_bytes, 16)
        except ValueError as e:
            raise ValueError(f'Invalid chunk size: {size_bytes!r}') from e

        if (mcs := self._config.max_content_chunk_size) is not None and self._chunk_remaining > mcs:
            raise ValueError(f'Content chunk size {self._chunk_remaining} exceeds maximum content chunk size: {mcs}')

        if self._chunk_remaining == 0:
            # Final chunk
            self._state = 'trailer'
        else:
            self._state = 'data'

        if len(self._header_buf) > 0:
            hb = self._header_buf
            self._header_buf = self._new_header_buf()

            for hb_mv in hb.segments():
                if not self._process(hb_mv, out):
                    return False

        if rem_mv is not None:
            if not self._process(rem_mv, out):
                return False

        return True

    def _process_data(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        mvl = len(mv)
        if mvl < self._chunk_remaining:
            self._chunk_remaining -= mvl
            out.append(self._adapter.make_content_chunk_data(mv))
            return True

        if self._chunk_remaining > 0:
            if mvl == self._chunk_remaining:
                out.append(self._adapter.make_content_chunk_data(mv))
                self._chunk_remaining = 0
                return True

            out.append(self._adapter.make_content_chunk_data(mv[:self._chunk_remaining]))
            mv = mv[self._chunk_remaining:]
            mvl = len(mv)
            self._chunk_remaining = 0

        if mvl < 1:
            return True

        if not self._got_cr:
            if mv[0] != 0x0d:
                raise ValueError(f'Expected \\r\\n after chunk data, got {bytes([mv[0]])!r}')
            self._got_cr = True
            mv = mv[1:]
            mvl -= 1
            if mvl < 1:
                return True

        if mv[0] != 0x0a:
            raise ValueError(f'Expected \\r\\n after chunk data, got {bytes([mv[0]])!r}')
        mv = mv[1:]
        mvl -= 1

        self._got_cr = False
        self._state = 'size'

        if mvl > 0:
            if not self._process(mv, out):
                return False

        return True

    def _process_trailer(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        mvl = len(mv)
        if mvl < 1:
            return True

        if not self._got_cr:
            if mv[0] != 0x0d:
                raise ValueError(f'Expected \\r\\n after final chunk, got {bytes([mv[0]])!r}')
            self._got_cr = True
            mv = mv[1:]
            mvl -= 1
            if mvl < 1:
                return True

        if mv[0] != 0x0a:
            raise ValueError(f'Expected \\r\\n after final chunk, got {bytes([mv[0]])!r}')
        mv = mv[1:]
        mvl -= 1

        del self._header_buf
        self._got_cr = False
        self._state = 'done'

        # Emit end marker
        out.append(self._adapter.make_end())

        if mvl > 0:
            out.append(mv)

        return True


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
"""


log, alog = get_module_loggers(globals())  # noqa


##


class AsyncioStreamPipelineChannelDriver(Abstract):
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['AsyncioStreamPipelineChannelDriver.Config']

        read_chunk_size: int = 0x10000
        write_chunk_max: ta.Optional[int] = None

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            spec: PipelineChannel.Spec,
            reader: asyncio.StreamReader,
            writer: ta.Optional[asyncio.StreamWriter] = None,
            config: ta.Optional[Config] = None,
            *,
            on_non_bytes_output: ta.Optional[ta.Callable[[ta.Any], ta.Awaitable[None]]] = None,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._reader = reader
        self._writer = writer
        if config is None:
            config = AsyncioStreamPipelineChannelDriver.Config.DEFAULT
        self._config = config

        self._on_non_bytes_output = on_non_bytes_output

        #

        self._shutdown_event = asyncio.Event()

        self._command_queue: asyncio.Queue[AsyncioStreamPipelineChannelDriver._Command] = asyncio.Queue()

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    @property
    def channel(self) -> PipelineChannel:
        return self._channel

    ##
    # init

    _sched: 'AsyncioStreamPipelineChannelDriver._Scheduling'

    _channel: PipelineChannel

    _flow: ta.Optional[ChannelPipelineFlow]

    _command_handlers: ta.Mapping[ta.Type['AsyncioStreamPipelineChannelDriver._Command'], ta.Callable[[ta.Any], ta.Awaitable[None]]]  # noqa
    _output_handlers: ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[None]]]

    async def _init(self) -> None:
        self._sched = self._Scheduling(self)

        services = PipelineChannel.Services.of(self._spec.services)
        self._flow = services.find(ChannelPipelineFlow)

        self._command_handlers = self._build_command_handlers()
        self._output_handlers = self._build_output_handlers()

        #

        self._channel = PipelineChannel(dc.replace(
            self._spec,
            services=(*self._spec.services, self._sched),
        ))

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

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}([{", ".join(map(repr, self.msgs))}])'

    async def _handle_command_feed_in(self, cmd: _FeedInCommand) -> None:
        async def _inner() -> None:
            self._channel.feed_in(*cmd.msgs)  # noqa

        await self._do_with_channel(_inner)

    async def feed_in(self, *msgs: ta.Any) -> None:
        check.state(not self._shutdown_event.is_set())

        self._command_queue.put_nowait(AsyncioStreamPipelineChannelDriver._FeedInCommand(msgs))

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
        if not self._want_read:
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
            in_msgs.append(ChannelPipelineFlowMessages.FlushInput())

        if eof:
            in_msgs.append(ChannelPipelineMessages.FinalInput())

        #

        async def _inner() -> None:
            self._channel.feed_in(*in_msgs)

        await self._do_with_channel(_inner)

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
        await self._command_queue.put(AsyncioStreamPipelineChannelDriver._UpdateWantReadCommand())

    _want_read = True

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
                in_cmd = AsyncioStreamPipelineChannelDriver._ReadCompletedCommand([
                    b
                    for pcr_cmd in self._pending_completed_reads
                    for b in pcr_cmd.data()
                ])
                self._command_queue.put_nowait(in_cmd)
                self._pending_completed_reads = None

            self._ensure_read_task()

    def _maybe_ensure_read_task(self) -> None:
        if (
                self._want_read or
                (self._flow is not None and self._flow.is_auto_read())
        ):
            self._ensure_read_task()

    @abc.abstractmethod
    def _ensure_read_task(self) -> None:
        raise NotImplementedError

    ##
    # scheduling

    class _Scheduling(ChannelPipelineScheduling):
        def __init__(self, d: 'AsyncioStreamPipelineChannelDriver') -> None:
            super().__init__()

            self._d = d

            self._pending: ta.List[ta.Tuple[float, ta.Callable[[], None]]] = []
            self._tasks: ta.Set[asyncio.Task] = set()

        class _Handle(ChannelPipelineScheduling.Handle):
            def cancel(self) -> None:
                raise NotImplementedError

        def schedule(
                self,
                handler_ref: ChannelPipelineHandlerRef,
                delay_s: float,
                fn: ta.Callable[[], None],
        ) -> ChannelPipelineScheduling.Handle:
            self._pending.append((delay_s, fn))
            return self._Handle()

        def cancel_all(self, handler_ref: ta.Optional[ChannelPipelineHandlerRef] = None) -> None:
            raise NotImplementedError

        async def _task_body(self, delay: float, fn: ta.Callable[[], None]) -> None:
            await asyncio.sleep(delay)

            self._d._command_queue.put_nowait(AsyncioStreamPipelineChannelDriver._ScheduledCommand(fn))  # noqa

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
            with self._channel.enter():
                cmd.fn()

        await self._do_with_channel(_inner)

    # handlers

    def _build_command_handlers(self) -> ta.Mapping[ta.Type[_Command], ta.Callable[[ta.Any], ta.Awaitable[None]]]:
        return {
            AsyncioStreamPipelineChannelDriver._FeedInCommand: self._handle_command_feed_in,
            AsyncioStreamPipelineChannelDriver._ReadCompletedCommand: self._handle_command_read_completed,
            AsyncioStreamPipelineChannelDriver._UpdateWantReadCommand: self._handle_command_update_want_read,
            AsyncioStreamPipelineChannelDriver._ScheduledCommand: self._handle_scheduled_command,
        }

    async def _handle_command(self, cmd: _Command) -> None:
        try:
            fn = self._command_handlers[cmd.__class__]
        except KeyError:
            raise TypeError(f'Unknown command type: {cmd.__class__}') from None

        await fn(cmd)

    ##
    # output handling

    # lifecycle

    async def _handle_output_final_output(self, msg: ChannelPipelineMessages.FinalOutput) -> None:
        self._shutdown_event.set()

        await self._close_writer()

    # data (special cased)

    async def _handle_output_bytes(self, msg: ta.Any) -> None:
        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._writer is not None and mv:
                self._writer.write(mv)

    # flow

    async def _handle_output_flush_output(self, msg: ChannelPipelineFlowMessages.FlushOutput) -> None:
        if self._writer is not None:
            await self._writer.drain()

    async def _handle_output_ready_for_input(self, msg: ChannelPipelineFlowMessages.ReadyForInput) -> None:
        await self._set_want_read(True)

    # async

    async def _handle_output_await(self, msg: AsyncChannelPipelineMessages.Await) -> None:
        try:
            result = await msg.obj

        except Exception as e:  # noqa
            with self._channel.enter():
                msg.set_failed(e)

        else:
            with self._channel.enter():
                msg.set_succeeded(result)

    # handlers

    def _build_output_handlers(self) -> ta.Mapping[type, ta.Callable[[ta.Any], ta.Awaitable[None]]]:
        return {
            ChannelPipelineMessages.FinalOutput: self._handle_output_final_output,

            ChannelPipelineFlowMessages.FlushOutput: self._handle_output_flush_output,
            ChannelPipelineFlowMessages.ReadyForInput: self._handle_output_ready_for_input,

            AsyncChannelPipelineMessages.Await: self._handle_output_await,
        }

    async def _handle_output(self, msg: ta.Any) -> None:
        if ByteStreamBuffers.can_bytes(msg):
            await self._handle_output_bytes(msg)
            return

        try:
            fn = self._output_handlers[msg.__class__]
        except KeyError:
            raise TypeError(f'Unknown output type: {msg.__class__}') from None

        await fn(msg)

    # execution helpers

    async def _do_with_channel(self, fn: ta.Callable[[], ta.Awaitable[None]]) -> None:
        prev_want_read = self._want_read
        if self._flow is not None and not self._flow.is_auto_read():
            self._want_read = False

        self._delay_sending_update_want_read_command = True
        try:
            await fn()

            await self._drain_channel_output()

        finally:
            self._delay_sending_update_want_read_command = False

        if self._shutdown_event.is_set():
            return

        await self._sched._flush_pending()  # noqa

        if self._want_read != prev_want_read:
            await self._send_update_want_read_command()

        self._maybe_ensure_read_task()

    async def _drain_channel_output(self) -> None:
        while (msg := self._channel.output.poll()) is not None:
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
                self._channel.destroy()

        finally:
            await self._cancel_tasks(self._shutdown_task, check_running=True)


##


class SimpleAsyncioStreamPipelineChannelDriver(AsyncioStreamPipelineChannelDriver):
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

            cmd: AsyncioStreamPipelineChannelDriver._Command
            try:
                data = task.result()
            except asyncio.CancelledError:
                cmd = AsyncioStreamPipelineChannelDriver._ReadCancelledCommand()  # noqa
            else:
                cmd = AsyncioStreamPipelineChannelDriver._ReadCompletedCommand(data)  # noqa

            self._command_queue.put_nowait(cmd)

            self._maybe_ensure_read_task()

        self._read_task.add_done_callback(_done)

    #

    async def _run(self) -> None:
        self._ensure_read_task()

        #

        command_queue_task: ta.Optional[asyncio.Task[AsyncioStreamPipelineChannelDriver._Command]] = None

        try:
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
# ../http/client/responses.py


##


class ResponsePipelineHttpDecodingMessageAdapter(PipelineHttpDecodingMessageAdapter):
    def make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def make_aborted(self, reason: str) -> ta.Any:
        return PipelineHttpResponseAborted(reason)

    def make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        return PipelineHttpResponseContentChunkData(data)

    def make_end(self) -> ta.Any:
        return PipelineHttpResponseEnd()


##


class PipelineHttpResponseDecoder(InboundBytesBufferingChannelPipelineHandler):
    """HTTP/1.x response head decoder."""

    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._decoder = PipelineHttpHeadDecoder(
            ResponsePipelineHttpDecodingMessageAdapter(),
            HttpParser.Mode.RESPONSE,
            config=config,
        )

    def inbound_buffered_bytes(self) -> int:
        return self._decoder.inbound_buffered_bytes()

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder.done:
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not ctx.services[ChannelPipelineFlow].is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            ctx.feed_in(msg)
            return

        for dec_msg in self._decoder.inbound(msg):
            ctx.feed_in(dec_msg)


##


class PipelineHttpResponseConditionalGzipDecoder(ChannelPipelineHandler):
    """
    Conditional streaming gzip decompression.

    Watches for DecodedHttpResponseHead; if Content-Encoding includes 'gzip', enable zlib decompressor for body bytes.
    Flushes on EOF.
    """

    def __init__(self) -> None:
        super().__init__()

        self._enabled = False
        self._z: ta.Optional[ta.Any] = None

    # FIXME:
    #  - we get obj.unconsumed_tail and unused_data, but not the full internal buffer sizes
    # def inbound_buffered_bytes(self) -> int:

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            if self._enabled and self._z is not None:
                tail = self._z.flush()
                if tail:
                    ctx.feed_in(tail)
            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpResponseHead):
            enc = msg.headers.lower.get('content-encoding', ())
            self._enabled = 'gzip' in enc
            self._z = zlib.decompressobj(16 + zlib.MAX_WBITS) if self._enabled else None
            ctx.feed_in(msg)
            return

        if (
                not self._enabled or
                self._z is None or
                not ByteStreamBuffers.can_bytes(msg)
        ):
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            out = self._z.decompress(mv)  # FIXME: max_length!! zip bombs
            # FIXME: also unconsumed_tail lol
            if out:
                ctx.feed_in(out)


##


class PipelineHttpResponseChunkedDecoder(InboundBytesBufferingChannelPipelineHandler):
    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config

        self._decoder: ta.Optional[ChunkedPipelineHttpContentChunkDecoder] = None

    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        if (dec := self._decoder) is None:
            return 0
        return dec.inbound_buffered_bytes()

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, PipelineHttpResponseHead):
            check.none(self._decoder)

            if msg.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
                self._decoder = ChunkedPipelineHttpContentChunkDecoder(
                    ResponsePipelineHttpDecodingMessageAdapter(),
                    config=self._config,
                )

            ctx.feed_in(msg)
            return

        if (dec := self._decoder) is None:
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not ctx.services[ChannelPipelineFlow].is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            ctx.feed_in(msg)
            return

        for dec_msg in dec.inbound(msg):
            ctx.feed_in(dec_msg)

        if dec.done:
            self._decoder = None


########################################
# ../http/server/requests.py


##


class RequestPipelineHttpDecodingMessageAdapter(PipelineHttpDecodingMessageAdapter):
    def make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        request = check.not_none(parsed.request_line)

        return PipelineHttpRequestHead(
            method=request.method,
            target=check.not_none(request.request_target).decode('utf-8'),
            version=request.http_version,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def make_aborted(self, reason: str) -> ta.Any:
        return PipelineHttpRequestAborted(reason)

    def make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        return PipelineHttpRequestContentChunkData(data)

    def make_end(self) -> ta.Any:
        return PipelineHttpRequestEnd()


##


class PipelineHttpRequestHeadDecoder(InboundBytesBufferingChannelPipelineHandler):
    """HTTP/1.x request head decoder."""

    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._decoder = PipelineHttpHeadDecoder(
            RequestPipelineHttpDecodingMessageAdapter(),
            HttpParser.Mode.REQUEST,
            config=config,
        )

    def inbound_buffered_bytes(self) -> int:
        return self._decoder.inbound_buffered_bytes()

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder.done:
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not ctx.services[ChannelPipelineFlow].is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            ctx.feed_in(msg)
            return

        for dec_msg in self._decoder.inbound(msg):
            ctx.feed_in(dec_msg)


##


class PipelineHttpRequestBodyAggregator(InboundBytesBufferingChannelPipelineHandler):
    """
    Aggregates an HTTP/1 request body using Content-Length.

    Input:
      - DecodedHttpRequestHead (from HttpRequestDecoder)
      - subsequent bytes-like chunks / views (body bytes)

    Output:
      - FullPipelineHttpRequest(head, body)

    Notes:
      - This is intentionally minimal:
        - Only supports Content-Length
        - No chunked transfer decoding
        - Assumes one request per connection in our server examples (we close after response)
      - Body bytes may arrive in the same TCP read as the head; HttpRequestDecoder forwards any remainder.

    TODO:
      - Use ContentLengthPipelineHttpContentChunkDecoder
    """

    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._cur_head: ta.Optional[PipelineHttpRequestHead] = None
        self._want = 0
        self._buf = SegmentedByteStreamBuffer(
            max_size=config.aggregated_body_buffer.max_size,
            chunk_size=config.aggregated_body_buffer.chunk_size,
        )

    def inbound_buffered_bytes(self) -> int:
        return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            # If we were expecting body bytes, that's a protocol error.
            if self._cur_head is not None and self._want and len(self._buf) < self._want:
                ctx.feed_in(PipelineHttpRequestAborted('EOF before HTTP request body complete'))

                self._cur_head = None
                self._want = 0
                self._buf.split_to(len(self._buf))

            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpRequestHead):
            if self._cur_head is not None:
                # We don't support pipelining in this minimal server.
                raise ValueError('HTTP pipelining not supported')

            self._cur_head = msg

            cl = msg.headers.single.get('content-length')
            if cl is None or cl == '':
                self._want = 0

            else:
                try:
                    self._want = int(cl)
                except ValueError:
                    raise ValueError('bad Content-Length') from None

                if self._want < 0:
                    raise ValueError('bad Content-Length')

                if (max_body := self._buf.max_size) is not None and self._want > max_body:
                    raise FrameTooLargeByteStreamBufferError('request body exceeded max_body')

            if self._want == 0:
                req = FullPipelineHttpRequest(msg, b'')
                self._cur_head = None
                self._want = 0
                ctx.feed_in(req)

            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        # Body bytes
        if self._cur_head is None:
            # Ignore stray bytes (or treat as error). Minimal server: ignore.
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        # If still not enough, just wait.
        if len(self._buf) < self._want:
            return

        # Extract exactly want bytes; preserve any extra (we don't support pipelining, but be correct).
        body_view = self._buf.split_to(self._want)
        body = body_view.tobytes()

        head = self._cur_head
        self._cur_head = None
        self._want = 0

        req = FullPipelineHttpRequest(head, body)
        ctx.feed_in(req)

        # If leftover bytes exist, treat as protocol error in our minimal server model.
        if len(self._buf):
            raise ValueError('unexpected extra bytes after request body')


##


class PipelineHttpRequestBodyStreamDecoder(InboundBytesBufferingChannelPipelineHandler):
    """
    Turns (PipelineHttpRequestHead + subsequent bytes) into streaming PipelineHttpContentChunk events +
    PipelineHttpRequestEnd.

    Supported body modes:
      - Content-Length: reads exactly that many bytes
      - Transfer-Encoding: chunked: decodes RFC 7230 chunked encoding (minimal, trailers ignored beyond terminator)
      - Neither present: treats body as "until EOF" (useful for infinite streaming uploads)
    """

    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config

        self._decoder: ta.Optional[PipelineHttpContentChunkDecoder] = None

    def inbound_buffered_bytes(self) -> int:
        if (dec := self._decoder) is None:
            return 0
        return dec.inbound_buffered_bytes()

    class _SelectedMode(ta.NamedTuple):
        mode: ta.Literal['none', 'eof', 'cl', 'chunked']
        length: ta.Optional[int]

    def _select_mode(self, head: PipelineHttpRequestHead) -> _SelectedMode:
        if head.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
            return self._SelectedMode('chunked', None)

        cl = head.headers.single.get('content-length')
        if cl is not None and cl != '':
            try:
                n = int(cl)
            except ValueError:
                raise ValueError('bad Content-Length') from None

            if n < 0:
                raise ValueError('bad Content-Length')

            if n == 0:
                return self._SelectedMode('none', None)

            return self._SelectedMode('cl', n)

        # No length info: treat as until EOF (supports infinite streaming).
        return self._SelectedMode('eof', None)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder is not None:
            if self._decoder.done:
                ctx.feed_in(msg)
                return

            if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
                if not ctx.services[ChannelPipelineFlow].is_auto_read():
                    ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

                ctx.feed_in(msg)
                return

            for dec_msg in self._decoder.inbound(msg):
                ctx.feed_in(dec_msg)

            return

        if not isinstance(msg, PipelineHttpRequestHead):
            ctx.feed_in(msg)
            return

        sm = self._select_mode(msg)

        ctx.feed_in(msg)

        if sm.mode == 'none':
            ctx.feed_in(PipelineHttpRequestEnd())

        elif sm.mode == 'eof':
            self._decoder = UntilFinalInputPipelineHttpContentChunkDecoder(
                RequestPipelineHttpDecodingMessageAdapter(),
                config=self._config,
            )

        elif sm.mode == 'cl':
            self._decoder = ContentLengthPipelineHttpContentChunkDecoder(
                RequestPipelineHttpDecodingMessageAdapter(),
                check.not_none(sm.length),
                config=self._config,
            )

        elif sm.mode == 'chunked':
            self._decoder = ChunkedPipelineHttpContentChunkDecoder(
                RequestPipelineHttpDecodingMessageAdapter(),
                config=self._config,
            )

        else:
            raise RuntimeError(f'unexpected mode {sm!r}')


########################################
# _amalg.py


##
