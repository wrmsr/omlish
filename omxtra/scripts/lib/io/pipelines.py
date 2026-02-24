#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../../../io/pipelines/_amalg.py
# @omlish-git-diff-omit
# ruff: noqa: FURB188 UP006 UP007 UP036 UP037 UP045
import abc
import collections
import dataclasses as dc
import functools
import inspect
import sys
import threading
import typing as ta


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


def __omlish_amalg__():  # noqa
    return dict(
        src_files=[
            dict(path='../../../omlish/io/streams/errors.py', sha1='67ca85fd8741b5bfefe76c872ce1c30c18fab06f'),
            dict(path='../../../omlish/lite/abstract.py', sha1='a2fc3f3697fa8de5247761e9d554e70176f37aac'),
            dict(path='../../../omlish/lite/check.py', sha1='df0ed561b5782545e34e61dd3424f69f836a87c0'),
            dict(path='../../../omlish/lite/namespaces.py', sha1='27b12b6592403c010fb8b2a0af7c24238490d3a1'),
            dict(path='errors.py', sha1='a6e20daf54f563f7d2aa4f28fce87fa06417facb'),
            dict(path='../../../omlish/io/streams/types.py', sha1='8a12dc29f6e483dd8df5336c0d9b58a00b64e7ed'),
            dict(path='core.py', sha1='b993ca754dc7ed762e0da07f3b05728d9ddac5ad'),
            dict(path='../../../omlish/io/streams/base.py', sha1='67ae88ffabae21210b5452fe49c9a3e01ca164c5'),
            dict(path='../../../omlish/io/streams/framing.py', sha1='dc2d7f638b042619fd3d95789c71532a29fd5fe4'),
            dict(path='../../../omlish/io/streams/utils.py', sha1='476363dfce81e3177a66f066892ed3fcf773ead8'),
            dict(path='bytes/buffering.py', sha1='aa8375c8ef0689db865bb4009afd3ed8dcc2bd12'),
            dict(path='flow/types.py', sha1='839f08718c67d2d84e56aee973ba1c9c34afb732'),
            dict(path='handlers/fns.py', sha1='75e982604574d6ffaacf9ac1f37ab6e9edbd608d'),
            dict(path='handlers/queues.py', sha1='53be6d12d02baa192d25fe4af3a0712ce6e62d6f'),
            dict(path='../../../omlish/io/streams/direct.py', sha1='83c33460e9490a77a00ae66251617ba98128b56b'),
            dict(path='../../../omlish/io/streams/scanning.py', sha1='4c0323e0b11cd506f7b6b4cf28ea4d7c6064b9d3'),
            dict(path='bytes/queues.py', sha1='38b11596cd0fa2367825252413923f1292c14f4e'),
            dict(path='handlers/flatmap.py', sha1='356703fad2cc24fb3b99bfadf46c6e2cbf62f539'),
            dict(path='../../../omlish/io/streams/segmented.py', sha1='f855d67d88ed71bbe2bbeee09321534f0ef18e24'),
            dict(path='bytes/decoders.py', sha1='d5fa28b723cdd66cc17e9a73632a51b9f031baf2'),
            dict(path='_amalg.py', sha1='f57d710297d549e3b788af08eeb44cf5ac1bab07'),
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

# ../../../omlish/io/streams/types.py
BytesLikeOrMemoryview = ta.Union[bytes, bytearray, memoryview]  # ta.TypeAlias

# core.py
F = ta.TypeVar('F')
ChannelPipelineHandlerFn = ta.Callable[['ChannelPipelineHandlerContext', F], T]  # ta.TypeAlias
ChannelPipelineHandlerT = ta.TypeVar('ChannelPipelineHandlerT', bound='ChannelPipelineHandler')
ShareableChannelPipelineHandlerT = ta.TypeVar('ShareableChannelPipelineHandlerT', bound='ShareableChannelPipelineHandler')  # noqa


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
        if not isinstance(v, self._unpack_isinstance_spec(spec)):
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
        spec = self._unpack_isinstance_spec(spec)

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
        if isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must not be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='isinstance(%s, %s)',
            )

        return v

    def of_not_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        spec = self._unpack_isinstance_spec(spec)

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
# ../../../../omlish/lite/namespaces.py


class NamespaceClass:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    def __init_subclass__(cls, **kwargs):  # noqa
        super().__init_subclass__(**kwargs)

        if any(issubclass(b, NamespaceClass) and b is not NamespaceClass for b in cls.__bases__):
            raise TypeError


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


@dc.dataclass(repr=False)
class MessageNotPropagatedChannelPipelineError(MessageChannelPipelineError, UnhandleableChannelPipelineError):
    pass


@dc.dataclass(repr=False)
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
# ../core.py


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
    def services(self) -> 'PipelineChannel._Services':  # noqa
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
            # Initial handlers are optional - handlers may be freely added and removed later.
            handlers: ta.Sequence[ChannelPipelineHandler] = (),

            config: Config = Config(),
            *,
            # Services are fixed for the lifetime of the channel.
            services: ta.Optional[ta.Sequence[ChannelPipelineService]] = None,
    ) -> None:
        super().__init__()

        self._config: ta.Final[PipelineChannel.Config] = config

        self._services: ta.Final[PipelineChannel._Services] = PipelineChannel._Services(services or [])

        self._out_q: ta.Final[collections.deque[ta.Any]] = collections.deque()

        self._saw_final_input = False
        self._saw_final_output = False

        self._execution_depth = 0

        self._deferred: collections.deque[PipelineChannel._Deferred] = collections.deque()

        self._propagation: PipelineChannel._Propagation = PipelineChannel._Propagation(self)

        #

        self._pipeline: ta.Final[ChannelPipeline] = ChannelPipeline(
            self,
            handlers,
            config=config.pipeline,
        )

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


########################################
# ../../../../omlish/io/streams/base.py


##


class BaseByteStreamBufferLike(ByteStreamBufferLike, Abstract):
    def _norm_slice(self, start: int, end: ta.Optional[int]) -> ta.Tuple[int, int]:
        s, e, _ = slice(start, end, 1).indices(len(self))
        if e < s:
            e = s
        return s, e


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

    #

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
                f', {self.fn!r}, '
                f'{f", else_fn={self.else_fn!r}" if self.else_fn is not None else ""}'
                f')'
            )

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.pred(ctx, msg):
                yield from self.fn(ctx, msg)
            elif (ef := self.else_fn) is not None:
                yield from ef(ctx, msg)
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

    @classmethod
    def drop(
            cls,
            direction: ChannelPipelineDirectionOrDuplex,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> ChannelPipelineHandler:
        fn = FlatMapChannelPipelineHandlerFns.drop()

        if filter is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(filter, fn)

        if filter_type is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(ChannelPipelineHandlerFns.isinstance(filter_type), fn)

        return cls.new(direction, fn)

    #

    @classmethod
    def feed_out_and_drop(
            cls,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> ChannelPipelineHandler:
        fn = FlatMapChannelPipelineHandlerFns.compose(
            FlatMapChannelPipelineHandlerFns.feed_out(),
            FlatMapChannelPipelineHandlerFns.drop(),
        )

        if filter is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(filter, fn)

        if filter_type is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(ChannelPipelineHandlerFns.isinstance(filter_type), fn)

        return cls.new('inbound', fn)


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
            max_bytes: ta.Optional[int] = None,
            chunk_size: int = 0,
            chunk_compact_threshold: float = .25,
    ) -> None:
        super().__init__()

        self._segs: ta.List[ta.Union[bytes, bytearray]] = []

        self._max_bytes = None if max_bytes is None else int(max_bytes)

        if chunk_size < 0:
            raise ValueError(chunk_size)
        self._chunk_size = chunk_size

        if not (0.0 <= chunk_compact_threshold <= 1.0):
            raise ValueError(chunk_compact_threshold)
        self._chunk_compact_threshold = chunk_compact_threshold

        self._active: ta.Optional[bytearray] = None
        self._active_used = 0

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

        return tuple(out)

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

        if self._max_bytes is not None and self._len + dl > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

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

            if self._max_bytes is not None and self._len + n > self._max_bytes:
                raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

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

        if self._max_bytes is not None and self._len + n > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

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
# ../bytes/decoders.py


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
            max_bytes=max_buffer,
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
            scanning: bool = False,
    ) -> None:
        super().__init__()

        self._scanning = scanning

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
        buf: MutableByteStreamBuffer = SegmentedByteStreamBuffer(chunk_size=0x4000)

        if self._scanning:
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
            scanning: bool = False,
    ) -> None:
        super().__init__(
            scanning=scanning,
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
# _amalg.py


##
