#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../../../../omlish/formats/yaml/goyaml/_amalg.py
# @omlish-git-diff-omit
# ruff: noqa: UP006 UP007 UP036 UP043 UP045
import abc
import base64
import collections
import copy
import dataclasses as dc
import datetime
import enum
import functools
import glob
import inspect
import io
import os.path
import sys
import threading
import typing as ta
import unicodedata


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


def __omlish_amalg__():  # noqa
    return dict(
        src_files=[
            dict(path='../../../lite/abstract.py', sha1='a2fc3f3697fa8de5247761e9d554e70176f37aac'),
            dict(path='../../../lite/check.py', sha1='5e625d74d4ad4e0492e25acac42820baa9956965'),
            dict(path='../../../lite/dataclasses.py', sha1='8b144d1d9474d96cf2a35f4db5cb224c30f538d6'),
            dict(path='errors.py', sha1='8fa73c90292f56f8faaedebb2f478ff6a3b95460'),
            dict(path='tokens.py', sha1='d52876a2a525bc99eb554fe28c3d27e7e01f43a9'),
            dict(path='ast.py', sha1='811593bad2d89bfecc4a688a8d5e92e66c026073'),
            dict(path='scanning.py', sha1='fe21556a59a30e12a110e85ef2b201a5d81f14d0'),
            dict(path='parsing.py', sha1='a7faf2bf497eec7087b2ee803b088af08d4b6cd0'),
            dict(path='decoding.py', sha1='03e29317ab0a76549db8e6938dfe83596dfe48df'),
            dict(path='_amalg.py', sha1='85989224f581528c4a189dca142cb3ec086ecd3c'),
        ],
    )


########################################


# ../../../lite/abstract.py
T = ta.TypeVar('T')

# ../../../lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# errors.py
YamlErrorOr = ta.Union['YamlError', T]  # ta.TypeAlias


########################################
# ../../../../lite/abstract.py


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
# ../../../../lite/check.py
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
# ../../../../lite/dataclasses.py


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
# ../errors.py


##


class YamlError(Exception, Abstract):
    @property
    @abc.abstractmethod
    def message(self) -> str:
        raise NotImplementedError


class EofYamlError(YamlError):
    @property
    def message(self) -> str:
        return 'eof'


@dc.dataclass()
class GenericYamlError(YamlError):
    obj: ta.Union[str, Exception]

    @property
    def message(self) -> str:
        if isinstance(self.obj, str):
            return self.obj
        else:
            return str(self.obj)


def yaml_error(obj: ta.Union[YamlError, str, Exception]) -> YamlError:
    if isinstance(obj, YamlError):
        return obj
    elif isinstance(obj, (str, Exception)):
        return GenericYamlError(obj)
    else:
        raise TypeError(obj)


########################################
# ../tokens.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


@dc.dataclass(frozen=True)
class YamlSyntaxError(YamlError):
    msg: str
    token: ta.Optional['YamlToken']

    @property
    def message(self) -> str:
        return self.msg


##


class YamlChars:
    # SEQUENCE_ENTRY character for sequence entry
    SEQUENCE_ENTRY = '-'
    # MAPPING_KEY character for mapping key
    MAPPING_KEY = '?'
    # MAPPING_VALUE character for mapping value
    MAPPING_VALUE = ':'
    # COLLECT_ENTRY character for collect entry
    COLLECT_ENTRY = ','
    # SEQUENCE_START character for sequence start
    SEQUENCE_START = '['
    # SEQUENCE_END character for sequence end
    SEQUENCE_END = ']'
    # MAPPING_START character for mapping start
    MAPPING_START = '{'
    # MAPPING_END character for mapping end
    MAPPING_END = '}'
    # COMMENT character for comment
    COMMENT = '#'
    # ANCHOR character for anchor
    ANCHOR = '&'
    # ALIAS character for alias
    ALIAS = '*'
    # TAG character for tag
    TAG = '!'
    # LITERAL character for literal
    LITERAL = '|'
    # FOLDED character for folded
    FOLDED = '>'
    # SINGLE_QUOTE character for single quote
    SINGLE_QUOTE = '\''
    # DOUBLE_QUOTE character for double quote
    DOUBLE_QUOTE = '"'
    # DIRECTIVE character for directive
    DIRECTIVE = '%'
    # SPACE character for space
    SPACE = ' '
    # LINE_BREAK character for line break
    LINE_BREAK = '\n'


class YamlTokenType(enum.Enum):
    # UNKNOWN reserve for invalid type
    UNKNOWN = enum.auto()
    # DOCUMENT_HEADER type for DocumentHeader token
    DOCUMENT_HEADER = enum.auto()
    # DOCUMENT_END type for DocumentEnd token
    DOCUMENT_END = enum.auto()
    # SEQUENCE_ENTRY type for SequenceEntry token
    SEQUENCE_ENTRY = enum.auto()
    # MAPPING_KEY type for MappingKey token
    MAPPING_KEY = enum.auto()
    # MAPPING_VALUE type for MappingValue token
    MAPPING_VALUE = enum.auto()
    # MERGE_KEY type for MergeKey token
    MERGE_KEY = enum.auto()
    # COLLECT_ENTRY type for CollectEntry token
    COLLECT_ENTRY = enum.auto()
    # SEQUENCE_START type for SequenceStart token
    SEQUENCE_START = enum.auto()
    # SEQUENCE_END type for SequenceEnd token
    SEQUENCE_END = enum.auto()
    # MAPPING_START type for MappingStart token
    MAPPING_START = enum.auto()
    # MAPPING_END type for MappingEnd token
    MAPPING_END = enum.auto()
    # COMMENT type for Comment token
    COMMENT = enum.auto()
    # ANCHOR type for Anchor token
    ANCHOR = enum.auto()
    # ALIAS type for Alias token
    ALIAS = enum.auto()
    # TAG type for Tag token
    TAG = enum.auto()
    # LITERAL type for Literal token
    LITERAL = enum.auto()
    # FOLDED type for Folded token
    FOLDED = enum.auto()
    # SINGLE_QUOTE type for SingleQuote token
    SINGLE_QUOTE = enum.auto()
    # DOUBLE_QUOTE type for DoubleQuote token
    DOUBLE_QUOTE = enum.auto()
    # DIRECTIVE type for Directive token
    DIRECTIVE = enum.auto()
    # SPACE type for Space token
    SPACE = enum.auto()
    # NULL type for Null token
    NULL = enum.auto()
    # IMPLICIT_NULL type for implicit Null token.
    # This is used when explicit keywords such as null or ~ are not specified. It is distinguished during encoding and
    # output as an empty string.
    IMPLICIT_NULL = enum.auto()
    # INFINITY type for Infinity token
    INFINITY = enum.auto()
    # NAN type for Nan token
    NAN = enum.auto()
    # INTEGER type for Integer token
    INTEGER = enum.auto()
    # BINARY_INTEGER type for BinaryInteger token
    BINARY_INTEGER = enum.auto()
    # OCTET_INTEGER type for OctetInteger token
    OCTET_INTEGER = enum.auto()
    # HEX_INTEGER type for HexInteger token
    HEX_INTEGER = enum.auto()
    # FLOAT type for Float token
    FLOAT = enum.auto()
    # STRING type for String token
    STRING = enum.auto()
    # BOOL type for Bool token
    BOOL = enum.auto()
    # INVALID type for invalid token
    INVALID = enum.auto()


class YamlCharType(enum.Enum):
    # INDICATOR type of indicator character
    INDICATOR = enum.auto()
    # WHITE-SPACE type of white space character
    WHITESPACE = enum.auto()
    # MISCELLANEOUS type of miscellaneous character
    MISCELLANEOUS = enum.auto()
    # ESCAPED type of escaped character
    ESCAPED = enum.auto()
    # INVALID type for an invalid token.
    INVALID = enum.auto()


class YamlIndicator(enum.Enum):
    # NOT not an indicator
    NOT = enum.auto()
    # BLOCK_STRUCTURE indicator for block structure ( '-', '?', ':' )
    BLOCK_STRUCTURE = enum.auto()
    # FLOW_COLLECTION indicator for flow collection ( '[', ']', '{', '}', ',' )
    FLOW_COLLECTION = enum.auto()
    # COMMENT indicator for comment ( '#' )
    COMMENT = enum.auto()
    # NODE_PROPERTY indicator for node property ( '!', '&', '*' )
    NODE_PROPERTY = enum.auto()
    # BLOCK_SCALAR indicator for block scalar ( '|', '>' )
    BLOCK_SCALAR = enum.auto()
    # QUOTED_SCALAR indicator for quoted scalar ( ''', '"' )
    QUOTED_SCALAR = enum.auto()
    # DIRECTIVE indicator for directive ( '%' )
    DIRECTIVE = enum.auto()
    # INVALID_USE_OF_RESERVED indicator for invalid use of reserved keyword ( '@', '`' )
    INVALID_USE_OF_RESERVED = enum.auto()


##


class YamlKeywords:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    RESERVED_NULL_KEYWORDS = (
        'null',
        'Null',
        'NULL',
        '~',
    )

    RESERVED_BOOL_KEYWORDS = (
        'true',
        'True',
        'TRUE',
        'false',
        'False',
        'FALSE',
    )

    # For compatibility with other YAML 1.1 parsers.
    # Note that we use these solely for encoding the bool value with quotes. go-yaml should not treat these as reserved
    # keywords at parsing time. as go-yaml is supposed to be compliant only with YAML 1.2.
    RESERVED_LEGACY_BOOL_KEYWORDS = (
        'y',
        'Y',
        'yes',
        'Yes',
        'YES',
        'n',
        'N',
        'no',
        'No',
        'NO',
        'on',
        'On',
        'ON',
        'off',
        'Off',
        'OFF',
    )

    RESERVED_INF_KEYWORDS = (
        '.inf',
        '.Inf',
        '.INF',
        '-.inf',
        '-.Inf',
        '-.INF',
    )

    RESERVED_NAN_KEYWORDS = (
        '.nan',
        '.NaN',
        '.NAN',
    )

    RESERVED_KEYWORD_MAP: ta.ClassVar[ta.Mapping[str, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']]]
    RESERVED_ENC_KEYWORD_MAP: ta.ClassVar[ta.Mapping[str, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']]]


def _yaml_reserved_keyword_token(typ: YamlTokenType, value: str, org: str, pos: 'YamlPosition') -> 'YamlToken':
    return YamlToken(
        type=typ,
        char_type=YamlCharType.MISCELLANEOUS,
        indicator=YamlIndicator.NOT,
        value=value,
        origin=org,
        position=pos,
    )


YamlKeywords.RESERVED_KEYWORD_MAP = {
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.NULL) for keyword in YamlKeywords.RESERVED_NULL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.BOOL) for keyword in YamlKeywords.RESERVED_BOOL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.INFINITY) for keyword in YamlKeywords.RESERVED_INF_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.NAN) for keyword in YamlKeywords.RESERVED_NAN_KEYWORDS},  # noqa
}


# RESERVED_ENC_KEYWORD_MAP contains is the keyword map used at encoding time.
# This is supposed to be a superset of RESERVED_KEYWORD_MAP, and used to quote legacy keywords present in YAML 1.1 or
# lesser for compatibility reasons, even though this library is supposed to be YAML 1.2-compliant.
YamlKeywords.RESERVED_ENC_KEYWORD_MAP = {
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.NULL) for keyword in YamlKeywords.RESERVED_NULL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.BOOL) for keyword in YamlKeywords.RESERVED_BOOL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.BOOL) for keyword in YamlKeywords.RESERVED_LEGACY_BOOL_KEYWORDS},  # noqa
}


##


YamlReservedTagKeyword = str  # ta.TypeAlias  # omlish-amalg-typing-no-move


class YamlReservedTagKeywords:
    # INTEGER `!!int` tag
    INTEGER = '!!int'
    # FLOAT `!!float` tag
    FLOAT = '!!float'
    # NULL `!!null` tag
    NULL = '!!null'
    # SEQUENCE `!!seq` tag
    SEQUENCE = '!!seq'
    # MAPPING `!!map` tag
    MAPPING = '!!map'
    # STRING `!!str` tag
    STRING = '!!str'
    # BINARY `!!binary` tag
    BINARY = '!!binary'
    # ORDERED_MAP `!!omap` tag
    ORDERED_MAP = '!!omap'
    # SET `!!set` tag
    SET = '!!set'
    # TIMESTAMP `!!timestamp` tag
    TIMESTAMP = '!!timestamp'
    # BOOLEAN `!!bool` tag
    BOOLEAN = '!!bool'
    # MERGE `!!merge` tag
    MERGE = '!!merge'


# RESERVED_TAG_KEYWORD_MAP map for reserved tag keywords
YAML_RESERVED_TAG_KEYWORD_MAP: ta.Mapping[YamlReservedTagKeyword, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']] = {  # noqa
    YamlReservedTagKeywords.INTEGER: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.FLOAT: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.NULL: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.SEQUENCE: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.MAPPING: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.STRING: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.BINARY: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.ORDERED_MAP: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.SET: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.TIMESTAMP: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.BOOLEAN: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.MERGE: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
}


##


class YamlNumberType(enum.Enum):
    DECIMAL = 'decimal'
    BINARY = 'binary'
    OCTET = 'octet'
    HEX = 'hex'
    FLOAT = 'float'


@dc.dataclass()
class YamlNumberValue:
    type: YamlNumberType
    value: ta.Any
    text: str


def yaml_to_number(value: str) -> ta.Optional[YamlNumberValue]:
    num = _yaml_to_number(value)
    if isinstance(num, YamlError):
        return None

    return num


def _yaml_is_number(value: str) -> bool:
    num = _yaml_to_number(value)
    if isinstance(num, YamlError):
        # var numErr *strconv.NumError
        # if errors.As(err, &numErr) && errors.Is(numErr.Err, strconv.ErrRange) {
        #     return true

        return False

    return num is not None


def _yaml_to_number(value: str) -> YamlErrorOr[ta.Optional[YamlNumberValue]]:
    if not value:
        return None

    if value.startswith('_'):
        return None

    dot_count = value.count('.')
    if dot_count > 1:
        return None

    is_negative = value.startswith('-')
    normalized = value.lstrip('+').lstrip('-').replace('_', '')

    typ: YamlNumberType
    base = 0

    if normalized.startswith('0x'):
        normalized = normalized.lstrip('0x')
        base = 16
        typ = YamlNumberType.HEX
    elif normalized.startswith('0o'):
        normalized = normalized.lstrip('0o')
        base = 8
        typ = YamlNumberType.OCTET
    elif normalized.startswith('0b'):
        normalized = normalized.lstrip('0b')
        base = 2
        typ = YamlNumberType.BINARY
    elif normalized.startswith('0') and len(normalized) > 1 and dot_count == 0:
        base = 8
        typ = YamlNumberType.OCTET
    elif dot_count == 1:
        typ = YamlNumberType.FLOAT
    else:
        typ = YamlNumberType.DECIMAL
        base = 10

    text = normalized
    if is_negative:
        text = '-' + text

    v: ta.Any
    if typ == YamlNumberType.FLOAT:
        try:
            v = float(text)
        except ValueError as e:
            return yaml_error(e)
    else:
        try:
            v = int(text, base)
        except ValueError as e:
            return yaml_error(e)

    return YamlNumberValue(
        type=typ,
        value=v,
        text=text,
    )


##


# This is a subset of the formats permitted by the regular expression defined at http:#yaml.org/type/timestamp.html.
# Note that time.Parse cannot handle: "2001-12-14 21:59:43.10 -5" from the examples.
YAML_TIMESTAMP_FORMATS = (
    '%Y-%m-%dT%H:%M:%S.%fZ',  # RFC3339Nano
    '%Y-%m-%dt%H:%M:%S.%fZ',  # RFC3339Nano with lower-case "t"
    '%Y-%m-%d %H:%M:%S',      # DateTime
    '%Y-%m-%d',               # DateOnly

    # Not in examples, but to preserve backward compatibility by quoting time values
    '%H:%M',
)


def _yaml_is_timestamp(value: str) -> bool:
    for format_str in YAML_TIMESTAMP_FORMATS:
        try:
            datetime.datetime.strptime(value, format_str)  # noqa
            return True
        except ValueError:
            continue
    return False


##


# is_need_quoted checks whether the value needs quote for passed string or not
def _yaml_is_need_quoted(value: str) -> bool:
    if not value:
        return True

    if value in YamlKeywords.RESERVED_ENC_KEYWORD_MAP:
        return True

    if _yaml_is_number(value):
        return True

    if value == '-':
        return True

    if value[0] in ('*', '&', '[', '{', '}', ']', ',', '!', '|', '>', '%', '\'', '"', '@', ' ', '`'):
        return True

    if value[-1] in (':', ' '):
        return True

    if _yaml_is_timestamp(value):
        return True

    for i, c in enumerate(value):
        if c in ('#', '\\'):
            return True
        elif c in (':', '-'):
            if i + 1 < len(value) and value[i + 1] == ' ':
                return True

    return False


# literal_block_header detect literal block scalar header
def yaml_literal_block_header(value: str) -> str:
    lbc = yaml_detect_line_break_char(value)

    if lbc not in value:
        return ''
    elif value.endswith(lbc + lbc):
        return '|+'
    elif value.endswith(lbc):
        return '|'
    else:
        return '|-'


##


# new create reserved keyword token or number token and other string token.
def yaml_new_token(value: str, org: str, pos: 'YamlPosition') -> 'YamlToken':
    fn = YamlKeywords.RESERVED_KEYWORD_MAP.get(value)
    if fn is not None:
        return fn(value, org, pos)

    if (num := yaml_to_number(value)) is not None:
        tk = YamlToken(
            type=YamlTokenType.INTEGER,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value=value,
            origin=org,
            position=pos,
        )
        if num.type == YamlNumberType.FLOAT:
            tk.type = YamlTokenType.FLOAT
        elif num.type == YamlNumberType.BINARY:
            tk.type = YamlTokenType.BINARY_INTEGER
        elif num.type == YamlNumberType.OCTET:
            tk.type = YamlTokenType.OCTET_INTEGER
        elif num.type == YamlNumberType.HEX:
            tk.type = YamlTokenType.HEX_INTEGER
        return tk

    return YamlTokenMakers.new_string(value, org, pos)


# Position type for position in YAML document
@dc.dataclass()
class YamlPosition:
    line: int
    column: int
    offset: int
    indent_num: int
    indent_level: int

    # String position to text
    def __str__(self) -> str:
        return f'[level:{self.indent_level:d},line:{self.line:d},column:{self.column:d},offset:{self.offset:d}]'


# Token type for token
@dc.dataclass()
@ta.final
class YamlToken:
    # Type is a token type.
    type: YamlTokenType
    # CharType is a character type.
    char_type: YamlCharType
    # Indicator is an indicator type.
    indicator: YamlIndicator
    # Value is a string extracted with only meaningful characters, with spaces and such removed.
    value: str
    # Origin is a string that stores the original text as-is.
    origin: str
    # Error keeps error message for InvalidToken.
    error: ta.Optional[YamlError] = None
    # Position is a token position.
    position: YamlPosition = dc.field(default_factory=dataclass_field_required('position'))
    # Next is a next token reference.
    next: ta.Optional['YamlToken'] = dc.field(default=None, repr=False)
    # Prev is a previous token reference.
    prev: ta.Optional['YamlToken'] = dc.field(default=None, repr=False)

    # previous_type previous token type
    def previous_type(self) -> YamlTokenType:
        if self.prev is not None:
            return self.prev.type

        return YamlTokenType.UNKNOWN

    # next_type next token type
    def next_type(self) -> YamlTokenType:
        if self.next is not None:
            return self.next.type

        return YamlTokenType.UNKNOWN

    # add_column append column number to current position of column
    @classmethod
    def add_column(cls, t: ta.Optional['YamlToken'], col: int) -> None:
        if t is None:
            return

        t.position.column += col

    # clone copy token ( preserve Prev/Next reference )
    @classmethod
    def clone(cls, t: ta.Optional['YamlToken']) -> ta.Optional['YamlToken']:
        if t is None:
            return None

        copied = copy.copy(t)
        if t.position is not None:
            pos = copy.copy(t.position)
            copied.position = pos

        return copied


##


# Tokens type of token collection
class YamlTokens(ta.List[YamlToken]):
    def invalid_token(self) -> ta.Optional[YamlToken]:
        for tt in self:
            if tt.type == YamlTokenType.INVALID:
                return tt
        return None

    def _add(self, tk: YamlToken) -> None:
        if not self:
            self.append(tk)
        else:
            last = self[-1]
            last.next = tk
            tk.prev = last
            self.append(tk)

    # add append new some tokens
    def add(self, *tks: YamlToken) -> None:
        for tk in tks:
            self._add(tk)


##


class YamlTokenMakers:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    # new_string create token for String
    @staticmethod
    def new_string(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.STRING,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value=value,
            origin=org,
            position=pos,
        )

    # new_sequence_entry create token for SequenceEntry
    @staticmethod
    def new_sequence_entry(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_ENTRY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.SEQUENCE_ENTRY,
            origin=org,
            position=pos,
        )

    # new_mapping_key create token for MappingKey
    @staticmethod
    def new_mapping_key(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_KEY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.MAPPING_KEY,
            origin=YamlChars.MAPPING_KEY,
            position=pos,
        )

    # new_mapping_value create token for MappingValue
    @staticmethod
    def new_mapping_value(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_VALUE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.MAPPING_VALUE,
            origin=YamlChars.MAPPING_VALUE,
            position=pos,
        )

    # new_collect_entry create token for CollectEntry
    @staticmethod
    def new_collect_entry(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.COLLECT_ENTRY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.COLLECT_ENTRY,
            origin=org,
            position=pos,
        )

    # new_sequence_start create token for SequenceStart
    @staticmethod
    def new_sequence_start(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_START,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.SEQUENCE_START,
            origin=org,
            position=pos,
        )

    # new_sequence_end create token for SequenceEnd
    @staticmethod
    def new_sequence_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_END,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.SEQUENCE_END,
            origin=org,
            position=pos,
        )

    # new_mapping_start create token for MappingStart
    @staticmethod
    def new_mapping_start(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_START,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.MAPPING_START,
            origin=org,
            position=pos,
        )

    # new_mapping_end create token for MappingEnd
    @staticmethod
    def new_mapping_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_END,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.MAPPING_END,
            origin=org,
            position=pos,
        )

    # new_comment create token for Comment
    @staticmethod
    def new_comment(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.COMMENT,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.COMMENT,
            value=value,
            origin=org,
            position=pos,
        )

    # new_anchor create token for Anchor
    @staticmethod
    def new_anchor(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.ANCHOR,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=YamlChars.ANCHOR,
            origin=org,
            position=pos,
        )

    # new_alias create token for Alias
    @staticmethod
    def new_alias(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.ALIAS,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=YamlChars.ALIAS,
            origin=org,
            position=pos,
        )

    # new_tag create token for Tag
    @staticmethod
    def new_tag(value: str, org: str, pos: YamlPosition) -> YamlToken:
        fn = YAML_RESERVED_TAG_KEYWORD_MAP.get(value)
        if fn is not None:
            return fn(value, org, pos)

        return YamlToken(
            type=YamlTokenType.TAG,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=value,
            origin=org,
            position=pos,
        )

    # new_literal create token for Literal
    @staticmethod
    def new_literal(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.LITERAL,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_folded create token for Folded
    @staticmethod
    def new_folded(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.FOLDED,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_single_quote create token for SingleQuote
    @staticmethod
    def new_single_quote(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SINGLE_QUOTE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.QUOTED_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_double_quote create token for DoubleQuote
    @staticmethod
    def new_double_quote(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOUBLE_QUOTE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.QUOTED_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_directive create token for Directive
    @staticmethod
    def new_directive(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DIRECTIVE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.DIRECTIVE,
            value=YamlChars.DIRECTIVE,
            origin=org,
            position=pos,
        )

    # new_space create token for Space
    @staticmethod
    def new_space(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SPACE,
            char_type=YamlCharType.WHITESPACE,
            indicator=YamlIndicator.NOT,
            value=YamlChars.SPACE,
            origin=YamlChars.SPACE,
            position=pos,
        )

    # new_merge_key create token for MergeKey
    @staticmethod
    def new_merge_key(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MERGE_KEY,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='<<',
            origin=org,
            position=pos,
        )

    # new_document_header create token for DocumentHeader
    @staticmethod
    def new_document_header(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOCUMENT_HEADER,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='---',
            origin=org,
            position=pos,
        )

    # new_document_end create token for DocumentEnd
    @staticmethod
    def new_document_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOCUMENT_END,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='...',
            origin=org,
            position=pos,
        )

    @staticmethod
    def new_invalid(err: YamlError, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.INVALID,
            char_type=YamlCharType.INVALID,
            indicator=YamlIndicator.NOT,
            value=org,
            origin=org,
            error=err,
            position=pos,
        )


##


# detect_line_break_char detect line break character in only one inside scalar content scope.
def yaml_detect_line_break_char(src: str) -> str:
    nc = src.count('\n')
    rc = src.count('\r')
    rnc = src.count('\r\n')
    if nc == rnc and rc == rnc:
        return '\r\n'
    elif rc > nc:
        return '\r'
    else:
        return '\n'


########################################
# ../ast.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


@dc.dataclass()
class UnexpectedNodeTypeYamlError(YamlError):
    actual: 'YamlNodeType'
    expected: 'YamlNodeType'
    token: YamlToken

    @property
    def message(self) -> str:
        return f'unexpected node type: expected {self.expected.name}, got {self.actual.name}, at {self.token.position}'


##


class YamlAstErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    INVALID_TOKEN_TYPE = yaml_error('invalid token type')
    INVALID_ANCHOR_NAME = yaml_error('invalid anchor name')
    INVALID_ALIAS_NAME = yaml_error('invalid alias name')


class YamlNodeType(enum.Enum):
    # UNKNOWN type identifier for default
    UNKNOWN = enum.auto()
    # DOCUMENT type identifier for document node
    DOCUMENT = enum.auto()
    # NULL type identifier for null node
    NULL = enum.auto()
    # BOOL type identifier for boolean node
    BOOL = enum.auto()
    # INTEGER type identifier for integer node
    INTEGER = enum.auto()
    # FLOAT type identifier for float node
    FLOAT = enum.auto()
    # INFINITY type identifier for infinity node
    INFINITY = enum.auto()
    # NAN type identifier for nan node
    NAN = enum.auto()
    # STRING type identifier for string node
    STRING = enum.auto()
    # MERGE_KEY type identifier for merge key node
    MERGE_KEY = enum.auto()
    # LITERAL type identifier for literal node
    LITERAL = enum.auto()
    # MAPPING type identifier for mapping node
    MAPPING = enum.auto()
    # MAPPING_KEY type identifier for mapping key node
    MAPPING_KEY = enum.auto()
    # MAPPING_VALUE type identifier for mapping value node
    MAPPING_VALUE = enum.auto()
    # SEQUENCE type identifier for sequence node
    SEQUENCE = enum.auto()
    # SEQUENCE_ENTRY type identifier for sequence entry node
    SEQUENCE_ENTRY = enum.auto()
    # ANCHOR type identifier for anchor node
    ANCHOR = enum.auto()
    # ALIAS type identifier for alias node
    ALIAS = enum.auto()
    # DIRECTIVE type identifier for directive node
    DIRECTIVE = enum.auto()
    # TAG type identifier for tag node
    TAG = enum.auto()
    # COMMENT type identifier for comment node
    COMMENT = enum.auto()
    # COMMENT_GROUP type identifier for comment group node
    COMMENT_GROUP = enum.auto()


# String node type identifier to YAML Structure name based on https://yaml.org/spec/1.2/spec.html
YAML_NODE_TYPE_YAML_NAMES: ta.Mapping[YamlNodeType, str] = {
    YamlNodeType.UNKNOWN: 'unknown',
    YamlNodeType.DOCUMENT: 'document',
    YamlNodeType.NULL: 'null',
    YamlNodeType.BOOL: 'boolean',
    YamlNodeType.INTEGER: 'int',
    YamlNodeType.FLOAT: 'float',
    YamlNodeType.INFINITY: 'inf',
    YamlNodeType.NAN: 'nan',
    YamlNodeType.STRING: 'string',
    YamlNodeType.MERGE_KEY: 'merge key',
    YamlNodeType.LITERAL: 'scalar',
    YamlNodeType.MAPPING: 'mapping',
    YamlNodeType.MAPPING_KEY: 'key',
    YamlNodeType.MAPPING_VALUE: 'value',
    YamlNodeType.SEQUENCE: 'sequence',
    YamlNodeType.SEQUENCE_ENTRY: 'value',
    YamlNodeType.ANCHOR: 'anchor',
    YamlNodeType.ALIAS: 'alias',
    YamlNodeType.DIRECTIVE: 'directive',
    YamlNodeType.TAG: 'tag',
    YamlNodeType.COMMENT: 'comment',
    YamlNodeType.COMMENT_GROUP: 'comment',
}


##


# Node type of node
class YamlNode(Abstract):
    # io.Reader

    def __str__(self) -> ta.NoReturn:
        raise TypeError

    @abc.abstractmethod
    def string(self) -> str:
        # FIXME: migrate off - ensure all sprintfy things explicitly call .string()
        raise NotImplementedError

    # get_token returns token instance
    @abc.abstractmethod
    def get_token(self) -> ta.Optional[YamlToken]:
        raise NotImplementedError

    # type returns type of node
    @abc.abstractmethod
    def type(self) -> YamlNodeType:
        raise NotImplementedError

    # add_column add column number to child nodes recursively
    @abc.abstractmethod
    def add_column(self, column: int) -> None:
        raise NotImplementedError

    # set_comment set comment token to node
    @abc.abstractmethod
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        raise NotImplementedError

    # comment returns comment token instance
    @abc.abstractmethod
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        raise NotImplementedError

    # get_path returns YAMLPath for the current node
    @abc.abstractmethod
    def get_path(self) -> str:
        raise NotImplementedError

    # set_path set YAMLPath for the current node
    @abc.abstractmethod
    def set_path(self, path: str) -> None:
        raise NotImplementedError

    # marshal_yaml
    @abc.abstractmethod
    def marshal_yaml(self) -> YamlErrorOr[str]:
        raise NotImplementedError

    # already read length
    @abc.abstractmethod
    def read_len(self) -> int:
        raise NotImplementedError

    # append read length
    @abc.abstractmethod
    def append_read_len(self, n: int) -> None:
        raise NotImplementedError

    # clean read length
    @abc.abstractmethod
    def clear_len(self) -> None:
        raise NotImplementedError


# MapKeyNode type for map key node
class MapKeyYamlNode(YamlNode, Abstract):
    @abc.abstractmethod
    def is_merge_key(self) -> bool:
        raise NotImplementedError

    # String node to text without comment
    @abc.abstractmethod
    def string_without_comment(self) -> str:
        raise NotImplementedError


# ScalarNode type for scalar node
class ScalarYamlNode(MapKeyYamlNode, Abstract):
    @abc.abstractmethod
    def get_value(self) -> ta.Any:
        raise NotImplementedError


##


@dc.dataclass()
class BaseYamlNode(YamlNode, Abstract):
    path: str = ''
    comment: ta.Optional['CommentGroupYamlNode'] = None
    cur_read: int = 0

    def read_len(self) -> int:
        return self.cur_read

    def clear_len(self) -> None:
        self.cur_read = 0

    def append_read_len(self, l: int) -> None:
        self.cur_read += l

    # get_path returns YAMLPath for the current node.
    @ta.final
    def get_path(self: ta.Optional['BaseYamlNode']) -> str:
        if self is None:
            return ''
        return self.path

    # set_path set YAMLPath for the current node.
    @ta.final
    def set_path(self: ta.Optional['BaseYamlNode'], path: str) -> None:
        if self is None:
            return
        self.path = path

    # get_comment returns comment token instance
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        return self.comment

    # set_comment set comment token
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        self.comment = node
        return None


def yaml_add_comment_string(base: str, node: 'CommentGroupYamlNode') -> str:
    return f'{base} {node.string()}'


##


def yaml_read_node(p: str, node: YamlNode) -> YamlErrorOr[int]:
    s = node.string()
    read_len = node.read_len()
    remain = len(s) - read_len
    if remain == 0:
        node.clear_len()
        return EofYamlError()

    size = min(remain, len(p))
    for idx, b in enumerate(s[read_len:read_len + size]):
        p[idx] = b  # type: ignore[index]  # FIXME: lol

    node.append_read_len(size)
    return size


def yaml_check_line_break(t: YamlToken) -> bool:
    if t.prev is not None:
        lbc = '\n'
        prev = t.prev
        adjustment = 0
        # if the previous type is sequence entry use the previous type for that
        if prev.type == YamlTokenType.SEQUENCE_ENTRY:
            # as well as switching to previous type count any new lines in origin to account for:
            # -
            #   b: c
            adjustment = t.origin.rstrip(lbc).count(lbc)
            if prev.prev is not None:
                prev = prev.prev

        line_diff = t.position.line - prev.position.line - 1
        if line_diff > 0:
            if prev.type == YamlTokenType.STRING:
                # Remove any line breaks included in multiline string
                adjustment += prev.origin.strip().rstrip(lbc).count(lbc)

            # Due to the way that comment parsing works its assumed that when a null value does not have new line in
            # origin it was squashed therefore difference is ignored.
            # foo:
            #  bar:
            #  # comment
            #  baz: 1
            # becomes
            # foo:
            #  bar: null # comment
            #
            #  baz: 1
            if prev.type in (YamlTokenType.NULL, YamlTokenType.IMPLICIT_NULL):
                return prev.origin.count(lbc) > 0

            if line_diff - adjustment > 0:
                return True

    return False


##


class YamlAsts:
    # Null create node for null value
    @classmethod
    def null(cls, tk: YamlToken) -> 'NullYamlNode':
        return NullYamlNode(
            token=tk,
        )

    _BOOL_TRUE_STRS: ta.ClassVar[ta.AbstractSet[str]] = {'1', 't', 'T', 'true', 'TRUE', 'True'}
    _BOOL_FALSE_STRS: ta.ClassVar[ta.AbstractSet[str]] = {'0', 'f', 'F', 'false', 'FALSE', 'False'}

    @classmethod
    def _parse_bool(cls, s: str) -> bool:
        if s in cls._BOOL_TRUE_STRS:
            return True
        if s in cls._BOOL_FALSE_STRS:
            return False
        raise ValueError(f'"{s}" is not a valid boolean string')

    # bool_ create node for boolean value
    @classmethod
    def bool_(cls, tk: YamlToken) -> 'BoolYamlNode':
        b = cls._parse_bool(tk.value)
        return BoolYamlNode(
            token=tk,
            value=b,
        )

    # integer create node for integer value
    @classmethod
    def integer(cls, tk: YamlToken) -> 'IntegerYamlNode':
        v: ta.Any = None
        if (num := yaml_to_number(tk.value)) is not None:
            v = num.value

        return IntegerYamlNode(
            token=tk,
            value=v,
        )

    # float_ create node for float value
    @classmethod
    def float_(cls, tk: YamlToken) -> 'FloatYamlNode':
        v: float = 0.
        if (num := yaml_to_number(tk.value)) is not None and num.type == YamlNumberType.FLOAT:
            if isinstance(num.value, float):
                v = num.value

        return FloatYamlNode(
            token=tk,
            value=v,
        )

    # infinity create node for .inf or -.inf value
    @classmethod
    def infinity(cls, tk: YamlToken) -> 'InfinityYamlNode':
        if tk.value in ('.inf', '.Inf', '.INF'):
            value = float('inf')
        elif tk.value in ('-.inf', '-.Inf', '-.INF'):
            value = float('-inf')
        node = InfinityYamlNode(
            token=tk,
            value=value,
        )
        return node

    # nan create node for .nan value
    @classmethod
    def nan(cls, tk: YamlToken) -> 'NanYamlNode':
        return NanYamlNode(
            token=tk,
        )

    # string create node for string value
    @classmethod
    def string(cls, tk: YamlToken) -> 'StringYamlNode':
        return StringYamlNode(
            token=tk,
            value=tk.value,
        )

    # comment create node for comment
    @classmethod
    def comment(cls, tk: ta.Optional[YamlToken]) -> 'CommentYamlNode':
        return CommentYamlNode(
            token=tk,
        )

    @classmethod
    def comment_group(cls, comments: ta.Iterable[ta.Optional[YamlToken]]) -> 'CommentGroupYamlNode':
        nodes: ta.List[CommentYamlNode] = []
        for c in comments:
            nodes.append(cls.comment(c))

        return CommentGroupYamlNode(
            comments=nodes,
        )

    # merge_key create node for merge key ( << )
    @classmethod
    def merge_key(cls, tk: YamlToken) -> 'MergeKeyYamlNode':
        return MergeKeyYamlNode(
            token=tk,
        )

    # mapping create node for map
    @classmethod
    def mapping(cls, tk: YamlToken, is_flow_style: bool, *values: 'MappingValueYamlNode') -> 'MappingYamlNode':
        node = MappingYamlNode(
            start=tk,
            is_flow_style=is_flow_style,
            values=[],
        )
        node.values.extend(values)
        return node

    # mapping_value create node for mapping value
    @classmethod
    def mapping_value(cls, tk: YamlToken, key: 'MapKeyYamlNode', value: YamlNode) -> 'MappingValueYamlNode':
        return MappingValueYamlNode(
            start=tk,
            key=key,
            value=value,
        )

    # mapping_key create node for map key ( '?' ).
    @classmethod
    def mapping_key(cls, tk: YamlToken) -> 'MappingKeyYamlNode':
        return MappingKeyYamlNode(
            start=tk,
        )

    # sequence create node for sequence
    @classmethod
    def sequence(cls, tk: YamlToken, is_flow_style: bool) -> 'SequenceYamlNode':
        return SequenceYamlNode(
            start=tk,
            is_flow_style=is_flow_style,
            values=[],
        )

    @classmethod
    def anchor(cls, tk: YamlToken) -> 'AnchorYamlNode':
        return AnchorYamlNode(
            start=tk,
        )

    @classmethod
    def alias(cls, tk: YamlToken) -> 'AliasYamlNode':
        return AliasYamlNode(
            start=tk,
        )

    @classmethod
    def document(cls, tk: ta.Optional[YamlToken], body: ta.Optional[YamlNode]) -> 'DocumentYamlNode':
        return DocumentYamlNode(
            start=tk,
            body=body,
        )

    @classmethod
    def directive(cls, tk: YamlToken) -> 'DirectiveYamlNode':
        return DirectiveYamlNode(
            start=tk,
        )

    @classmethod
    def literal(cls, tk: YamlToken) -> 'LiteralYamlNode':
        return LiteralYamlNode(
            start=tk,
        )

    @classmethod
    def tag(cls, tk: YamlToken) -> 'TagYamlNode':
        return TagYamlNode(
            start=tk,
        )


##


# File contains all documents in YAML file
@dc.dataclass()
class YamlFile:
    name: str = ''
    docs: ta.List['DocumentYamlNode'] = dc.field(default_factory=list)

    # read implements (io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        for doc in self.docs:
            n = doc.read(p)
            if isinstance(n, EofYamlError):
                continue
            return n
        return EofYamlError()

    # string all documents to text
    def string(self) -> str:
        docs: ta.List[str] = []
        for doc in self.docs:
            docs.append(doc.string())
        if len(docs) > 0:
            return '\n'.join(docs) + '\n'
        else:
            return ''


##


# DocumentNode type of Document
@dc.dataclass()
class DocumentYamlNode(BaseYamlNode):
    start: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('start'))  # position of DocumentHeader ( `---` )  # noqa
    end: ta.Optional[YamlToken] = None  # position of DocumentEnd ( `...` )
    body: ta.Optional[YamlNode] = dc.field(default_factory=dataclass_field_required('body'))

    # read implements (io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns DocumentNodeType
    def type(self) -> YamlNodeType:
        return YamlNodeType.DOCUMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return check.not_none(self.body).get_token()

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.body is not None:
            self.body.add_column(col)

    # string document to text
    def string(self) -> str:
        doc: ta.List[str] = []
        if self.start is not None:
            doc.append(self.start.value)
        if self.body is not None:
            doc.append(self.body.string())
        if self.end is not None:
            doc.append(self.end.value)
        return '\n'.join(doc)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# NullNode type of null node
@dc.dataclass()
class NullYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns NullType
    def type(self) -> YamlNodeType:
        return YamlNodeType.NULL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns nil value
    def get_value(self) -> ta.Any:
        return None

    # String returns `null` text
    def string(self) -> str:
        if self.token.type == YamlTokenType.IMPLICIT_NULL:
            if self.comment is not None:
                return self.comment.string()
            return ''
        if self.comment is not None:
            return yaml_add_comment_string('null', self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return 'null'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# IntegerNode type of integer node
@dc.dataclass()
class IntegerYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: ta.Any = dc.field(default_factory=dataclass_field_required('value'))  # int64 or uint64 value

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns IntegerType
    def type(self) -> YamlNodeType:
        return YamlNodeType.INTEGER

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns int64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String int64 to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# FloatNode type of float node
@dc.dataclass()
class FloatYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    precision: int = 0
    value: float = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns FloatType
    def type(self) -> YamlNodeType:
        return YamlNodeType.FLOAT

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns float64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String float64 to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


def _yaml_go_is_print(char_ord):
    """
    Approximates Go's unicode.IsPrint logic. A rune is printable if it is a letter, mark, number, punctuation, symbol,
    or ASCII space. (Corresponds to Unicode categories L, M, N, P, S, plus U+0020 SPACE).
    """

    if char_ord == 0x20:  # ASCII space
        return True
    # Check if the character is in categories L, M, N, P, S (Graphic characters)
    category = unicodedata.category(chr(char_ord))
    if category.startswith(('L', 'M', 'N', 'P', 'S')):
        return True
    return False


def _yaml_strconv_quote(s: str) -> str:
    """
    Produces a double-quoted string literal with Go-style escapes, similar to Go's strconv.Quote.
    """

    res = ['"']
    for char_val in s:
        char_ord = ord(char_val)

        if char_val == '"':
            res.append('\\"')
        elif char_val == '\\':
            res.append('\\\\')
        elif char_val == '\a':
            res.append('\\a')
        elif char_val == '\b':
            res.append('\\b')
        elif char_val == '\f':
            res.append('\\f')
        elif char_val == '\n':
            res.append('\\n')
        elif char_val == '\r':
            res.append('\\r')
        elif char_val == '\t':
            res.append('\\t')
        elif char_val == '\v':
            res.append('\\v')
        elif char_ord < 0x20 or char_ord == 0x7F:  # C0 controls and DEL
            res.append(f'\\x{char_ord:02x}')
        elif 0x20 <= char_ord < 0x7F:  # Printable ASCII (already handled \, ")
            res.append(char_val)
        # Unicode characters (char_ord >= 0x80) and C1 controls (0x80-0x9F)
        elif _yaml_go_is_print(char_ord):
            res.append(char_val)
        elif char_ord <= 0xFFFF:
            res.append(f'\\u{char_ord:04x}')
        else:
            res.append(f'\\U{char_ord:08x}')

    res.append('"')
    return ''.join(res)


##


# StringNode type of string node
@dc.dataclass()
class StringYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: str = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns StringType
    def type(self) -> YamlNodeType:
        return YamlNodeType.STRING

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.value

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False

    # string string value to text with quote or literal header if required
    def string(self) -> str:
        if self.token.type == YamlTokenType.SINGLE_QUOTE:
            quoted = _yaml_escape_single_quote(self.value)
            if self.comment is not None:
                return yaml_add_comment_string(quoted, self.comment)
            return quoted
        elif self.token.type == YamlTokenType.DOUBLE_QUOTE:
            quoted = _yaml_strconv_quote(self.value)
            if self.comment is not None:
                return yaml_add_comment_string(quoted, self.comment)
            return quoted

        lbc = yaml_detect_line_break_char(self.value)
        if lbc in self.value:
            # This block assumes that the line breaks in this inside scalar content and the Outside scalar content are
            # the same. It works mostly, but inconsistencies occur if line break characters are mixed.
            header = yaml_literal_block_header(self.value)
            space = ' ' * (self.token.position.column - 1)
            indent = ' ' * self.token.position.indent_num
            values: ta.List[str] = []
            for v in self.value.split(lbc):
                values.append(f'{space}{indent}{v}')
            block = lbc.join(values).rstrip(f'{lbc}{indent}{space}').rstrip(f'{indent}{space}')
            return f'{header}{lbc}{block}'
        elif len(self.value) > 0 and (self.value[0] == '{' or self.value[0] == '['):
            return f"'{self.value}'"
        if self.comment is not None:
            return yaml_add_comment_string(self.value, self.comment)
        return self.value

    def string_without_comment(self) -> str:
        if self.token.type == YamlTokenType.SINGLE_QUOTE:
            quoted = f"'{self.value}'"
            return quoted
        elif self.token.type == YamlTokenType.DOUBLE_QUOTE:
            quoted = _yaml_strconv_quote(self.value)
            return quoted

        lbc = yaml_detect_line_break_char(self.value)
        if lbc in self.value:
            # This block assumes that the line breaks in this inside scalar content and the Outside scalar content are
            # the same. It works mostly, but inconsistencies occur if line break characters are mixed.
            header = yaml_literal_block_header(self.value)
            space = ' ' * (self.token.position.column - 1)
            indent = ' ' * self.token.position.indent_num
            values: ta.List[str] = []
            for v in self.value.split(lbc):
                values.append(f'{space}{indent}{v}')
            block = lbc.join(values).rstrip(f'{lbc}{indent}{space}').rstrip(f'  {space}')
            return f'{header}{lbc}{block}'
        elif len(self.value) > 0 and (self.value[0] == '{' or self.value[0] == '['):
            return f"'{self.value}'"
        return self.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


# escape_single_quote escapes s to a single quoted scalar.
# https://yaml.org/spec/1.2.2/#732-single-quoted-style
def _yaml_escape_single_quote(s: str) -> str:
    sb = io.StringIO()
    # growLen = len(s) + # s includes also one ' from the doubled pair
    #     2 + # opening and closing '
    #     strings.Count(s, "'") # ' added by ReplaceAll
    # sb.Grow(growLen)
    sb.write("'")
    sb.write(s.replace("'", "''"))
    sb.write("'")
    return sb.getvalue()


##


# LiteralNode type of literal node
@dc.dataclass()
class LiteralYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional['StringYamlNode'] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns LiteralType
    def type(self) -> YamlNodeType:
        return YamlNodeType.LITERAL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.string()

    # String literal to text
    def string(self) -> str:
        origin = check.not_none(check.not_none(self.value).get_token()).origin
        lit = origin.rstrip(' ').rstrip('\n')
        if self.comment is not None:
            return f'{self.start.value} {self.comment.string()}\n{lit}'
        return f'{self.start.value}\n{lit}'

    def string_without_comment(self) -> str:
        return self.string()

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MergeKeyNode type of merge key node
@dc.dataclass()
class MergeKeyYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MergeKeyType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MERGE_KEY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # get_value returns '<<' value
    def get_value(self) -> ta.Any:
        return self.token.value

    # String returns '<<' value
    def string(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return str(self)

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return True


##


# BoolNode type of boolean node
@dc.dataclass()
class BoolYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: bool = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns BoolType
    def type(self) -> YamlNodeType:
        return YamlNodeType.BOOL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns boolean value
    def get_value(self) -> ta.Any:
        return self.value

    # String boolean to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# InfinityNode type of infinity node
@dc.dataclass()
class InfinityYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: float = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns InfinityType
    def type(self) -> YamlNodeType:
        return YamlNodeType.INFINITY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns math.Inf(0) or math.Inf(-1)
    def get_value(self) -> ta.Any:
        return self.value

    # String infinity to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# NanNode type of nan node
@dc.dataclass()
class NanYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns NanType
    def type(self) -> YamlNodeType:
        return YamlNodeType.NAN

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns math.NaN()
    def get_value(self) -> ta.Any:
        return float('nan')

    # String returns .nan
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MapNode interface of MappingValueNode / MappingNode
class MapYamlNode(Abstract):
    @abc.abstractmethod
    def map_range(self) -> 'MapYamlNodeIter':
        raise NotImplementedError


YAML_START_RANGE_INDEX = -1


# MapNodeIter is an iterator for ranging over a MapNode
@dc.dataclass()
class MapYamlNodeIter:
    values: ta.List['MappingValueYamlNode']
    idx: int

    # next advances the map iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # key returns the key of the iterator's current map node entry.
    def key(self) -> MapKeyYamlNode:
        return self.values[self.idx].key

    # value returns the value of the iterator's current map node entry.
    def value(self) -> YamlNode:
        return self.values[self.idx].value

    # key_value returns the MappingValueNode of the iterator's current map node entry.
    def key_value(self) -> 'MappingValueYamlNode':
        return self.values[self.idx]


#


# MappingNode type of mapping node
@dc.dataclass()
class MappingYamlNode(MapYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    end: ta.Optional[YamlToken] = None
    is_flow_style: bool = dc.field(default_factory=dataclass_field_required('is_flow_style'))
    values: ta.List['MappingValueYamlNode'] = dc.field(default_factory=dataclass_field_required('values'))
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None

    def start_pos(self) -> YamlPosition:
        if len(self.values) == 0:
            return self.start.position
        return check.not_none(self.values[0].key.get_token()).position

    # merge merge key/value of map.
    def merge(self, target: 'MappingYamlNode') -> None:
        key_to_map_value_map: ta.Dict[str, MappingValueYamlNode] = {}
        for value in self.values:
            key = value.key.string()
            key_to_map_value_map[key] = value
        column = self.start_pos().column - target.start_pos().column
        target.add_column(column)
        for value in target.values:
            map_value = key_to_map_value_map.get(value.key.string())
            if map_value is not None:
                map_value.value = value.value
            else:
                self.values.append(value)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        for value in self.values:
            value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MappingType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        YamlToken.add_column(self.end, col)
        for value in self.values:
            value.add_column(col)

    def flow_style_string(self, comment_mode: bool) -> str:
        values: ta.List[str] = []
        for value in self.values:
            values.append(value.string().lstrip(' '))
        map_text = f'{{{", ".join(values)}}}'
        if comment_mode and self.comment is not None:
            return yaml_add_comment_string(map_text, self.comment)
        return map_text

    def block_style_string(self, comment_mode: bool) -> str:
        values: ta.List[str] = []
        for value0 in self.values:
            values.append(value0.string())
        map_text = '\n'.join(values)
        if comment_mode and self.comment is not None:
            value1 = values[0]
            space_num = 0
            for i in range(len(value1)):
                if value1[i] != ' ':
                    break
                space_num += 1
            comment = self.comment.string_with_space(space_num)
            return f'{comment}\n{map_text}'
        return map_text

    # String mapping values to text
    def string(self) -> str:
        if len(self.values) == 0:
            if self.comment is not None:
                return yaml_add_comment_string('{}', self.comment)
            return '{}'

        comment_mode = True
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string(comment_mode)

        return self.block_style_string(comment_mode)

    # map_range implements MapNode protocol
    def map_range(self) -> MapYamlNodeIter:
        return MapYamlNodeIter(
            idx=YAML_START_RANGE_INDEX,
            values=self.values,
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# MappingKeyNode type of tag node
@dc.dataclass()
class MappingKeyYamlNode(MapKeyYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MappingKeyType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING_KEY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def string(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return f'{self.start.value} {check.not_none(self.value).string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()


##


# MappingValueNode type of mapping value
@dc.dataclass()
class MappingValueYamlNode(MapYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))  # delimiter token ':'.
    collect_entry: ta.Optional[YamlToken] = None  # collect entry token ','.
    key: MapKeyYamlNode = dc.field(default_factory=dataclass_field_required('key'))
    value: YamlNode = dc.field(default_factory=dataclass_field_required('value'))
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None
    is_flow_style: bool = False

    # Replace replace value node.
    def replace(self, value: YamlNode) -> ta.Optional[YamlError]:
        column = check.not_none(self.value.get_token()).position.column - check.not_none(value.get_token()).position.column  # noqa
        value.add_column(column)
        self.value = value
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MappingValueType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING_VALUE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.key is not None:
            self.key.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        if isinstance(self.value, MappingYamlNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, MappingValueYamlNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, SequenceYamlNode):
            self.value.set_is_flow_style(is_flow)

    # String mapping value to text
    def string(self) -> str:
        text: str
        if self.comment is not None:
            text = f'{self.comment.string_with_space(check.not_none(self.key.get_token()).position.column - 1)}\n{self.to_string()}'  # noqa
        else:
            text = self.to_string()

        if self.foot_comment is not None:
            text += f'\n{self.foot_comment.string_with_space(check.not_none(self.key.get_token()).position.column - 1)}'

        return text

    def to_string(self) -> str:
        space = ' ' * (check.not_none(self.key.get_token()).position.column - 1)
        if yaml_check_line_break(check.not_none(self.key.get_token())):
            space = f'\n{space}'

        key_indent_level = check.not_none(self.key.get_token()).position.indent_level
        value_indent_level = check.not_none(self.value.get_token()).position.indent_level
        key_comment = self.key.get_comment()

        if isinstance(self.value, ScalarYamlNode):
            value = self.value.string()
            if value == '':
                # implicit null value.
                return f'{space}{self.key.string()}:'
            return f'{space}{self.key.string()}: {value}'

        elif key_indent_level < value_indent_level and not self.is_flow_style:
            value_str = self.value.string()
            # For flow-style values indented on the next line, we need to add the proper indentation
            if isinstance(self.value, MappingYamlNode) and self.value.is_flow_style:
                value_indent = ' ' * (self.value.get_token().position.column - 1)
                value_str = value_indent + value_str
            elif isinstance(self.value, SequenceYamlNode) and self.value.is_flow_style:
                value_indent = ' ' * (self.value.get_token().position.column - 1)
                value_str = value_indent + value_str
            if key_comment is not None:
                return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{value_str}'

            return f'{space}{self.key.string()}:\n{value_str}'

        elif isinstance(self.value, MappingYamlNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, SequenceYamlNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AnchorYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AliasYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, TagYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        if key_comment is not None:
            return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{self.value.string()}'

        if isinstance(self.value, MappingYamlNode) and self.value.comment is not None:
            return f'{space}{self.key.string()}: {self.value.string().lstrip(" ")}'

        return f'{space}{self.key.string()}:\n{self.value.string()}'

    # map_range implements MapNode protocol
    def map_range(self) -> MapYamlNodeIter:
        return MapYamlNodeIter(
            idx=YAML_START_RANGE_INDEX,
            values=[self],
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# ArrayNode interface of SequenceNode
class ArrayYamlNode(YamlNode, Abstract):
    @abc.abstractmethod
    def array_range(self) -> ta.Optional['ArrayYamlNodeIter']:
        raise NotImplementedError


# ArrayNodeIter is an iterator for ranging over a ArrayNode
@dc.dataclass()
class ArrayYamlNodeIter:
    values: ta.List[YamlNode]
    idx: int

    # next advances the array iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # Value returns the value of the iterator's current array entry.
    def value(self) -> YamlNode:
        return self.values[self.idx]

    # len returns length of array
    def len(self) -> int:
        return len(self.values)


##


# SequenceNode type of sequence node
@dc.dataclass()
class SequenceYamlNode(BaseYamlNode, ArrayYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    end: ta.Optional[YamlToken] = None
    is_flow_style: bool = dc.field(default_factory=dataclass_field_required('is_flow_style'))
    values: ta.List[ta.Optional[YamlNode]] = dc.field(default_factory=dataclass_field_required('values'))
    value_head_comments: ta.List[ta.Optional['CommentGroupYamlNode']] = dc.field(default_factory=list)
    entries: ta.List['SequenceEntryYamlNode'] = dc.field(default_factory=list)
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None

    # replace replace value node.
    def replace(self, idx: int, value: YamlNode) -> ta.Optional[YamlError]:
        if len(self.values) <= idx:
            return yaml_error(f'invalid index for sequence: sequence length is {len(self.values):d}, but specified {idx:d} index')  # noqa

        column = check.not_none(check.not_none(self.values[idx]).get_token()).position.column - check.not_none(value.get_token()).position.column  # noqa
        value.add_column(column)
        self.values[idx] = value
        return None

    # merge merge sequence value.
    def merge(self, target: 'SequenceYamlNode') -> None:
        column = self.start.position.column - target.start.position.column
        target.add_column(column)
        self.values.extend(target.values)
        if len(target.value_head_comments) == 0:
            self.value_head_comments.extend([None] * len(target.values))
            return

        self.value_head_comments.extend(target.value_head_comments)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        for value in self.values:
            if isinstance(value, MappingYamlNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, MappingValueYamlNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, SequenceYamlNode):
                value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns SequenceType
    def type(self) -> YamlNodeType:
        return YamlNodeType.SEQUENCE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        YamlToken.add_column(self.end, col)
        for value in self.values:
            check.not_none(value).add_column(col)

    def flow_style_string(self) -> str:
        values: ta.List[str] = []
        for value in self.values:
            values.append(check.not_none(value).string())

        seq_text = f'[{", ".join(values)}]'
        if self.comment is not None:
            return yaml_add_comment_string(seq_text, self.comment)

        return seq_text

    def block_style_string(self) -> str:
        space = ' ' * (self.start.position.column - 1)
        values: ta.List[str] = []
        if self.comment is not None:
            values.append(self.comment.string_with_space(self.start.position.column - 1))

        for idx, value in enumerate(self.values):
            if value is None:
                continue

            value_str = value.string()
            new_line_prefix = ''
            if value_str.startswith('\n'):
                value_str = value_str[1:]
                new_line_prefix = '\n'

            splitted_values = value_str.split('\n')
            trimmed_first_value = splitted_values[0].lstrip(' ')
            diff_length = len(splitted_values[0]) - len(trimmed_first_value)
            if (
                    (len(splitted_values) > 1 and value.type() == YamlNodeType.STRING) or
                    value.type() == YamlNodeType.LITERAL
            ):
                # If multi-line string, the space characters for indent have already been added, so delete them.
                prefix = space + '  '
                for i in range(1, len(splitted_values)):
                    splitted_values[i] = splitted_values[i].lstrip(prefix)

            new_values: ta.List[str] = [trimmed_first_value]
            for i in range(1, len(splitted_values)):
                if len(splitted_values[i]) <= diff_length:
                    # this line is \n or white space only
                    new_values.append('')
                    continue

                trimmed = splitted_values[i][diff_length:]
                new_values.append(f'{space}  {trimmed}')

            new_value = '\n'.join(new_values)
            if len(self.value_head_comments) == len(self.values) and self.value_head_comments[idx] is not None:
                values.append(
                    f'{new_line_prefix}'
                    f'{check.not_none(self.value_head_comments[idx]).string_with_space(self.start.position.column - 1)}',  # noqa
                )
                new_line_prefix = ''

            values.append(f'{new_line_prefix}{space}- {new_value}')

        if self.foot_comment is not None:
            values.append(self.foot_comment.string_with_space(self.start.position.column - 1))

        return '\n'.join(values)

    # String sequence to text
    def string(self) -> str:
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string()
        return self.block_style_string()

    # array_range implements ArrayNode protocol
    def array_range(self) -> ta.Optional[ArrayYamlNodeIter]:
        return ArrayYamlNodeIter(
            idx=YAML_START_RANGE_INDEX,
            values=ta.cast('ta.List[YamlNode]', self.values),
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# SequenceEntryNode is the sequence entry.
@dc.dataclass()
class SequenceEntryYamlNode(BaseYamlNode):
    head_comment: ta.Optional['CommentGroupYamlNode'] = dc.field(default_factory=dataclass_field_required('head_commend'))  # head comment.  # noqa
    line_comment: ta.Optional['CommentGroupYamlNode'] = None  # line comment e.g.) - # comment.
    start: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('start'))  # entry token.
    value: YamlNode = dc.field(default_factory=dataclass_field_required('value'))  # value node.

    # String node to text
    def string(self) -> str:
        return ''  # TODO

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return self.start

    # type returns type of node
    def type(self) -> YamlNodeType:
        return YamlNodeType.SEQUENCE_ENTRY

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)

    # set_comment set line comment.
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        self.line_comment = node
        return None

    # comment returns comment token instance
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        return self.line_comment

    # marshal_yaml
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)


# sequence_entry creates SequenceEntryNode instance.
def yaml_sequence_entry(
        start: ta.Optional[YamlToken],
        value: YamlNode,
        head_comment: ta.Optional['CommentGroupYamlNode'],
) -> SequenceEntryYamlNode:
    return SequenceEntryYamlNode(
        head_comment=head_comment,
        start=start,
        value=value,
    )


# SequenceMergeValue creates SequenceMergeValueNode instance.
def yaml_sequence_merge_value(*values: MapYamlNode) -> 'SequenceMergeValueYamlNode':
    return SequenceMergeValueYamlNode(
        values=list(values),
    )


##


# SequenceMergeValueNode is used to convert the Sequence node specified for the merge key into a MapNode format.
@dc.dataclass()
class SequenceMergeValueYamlNode(MapYamlNode):
    values: ta.List[MapYamlNode] = dc.field(default_factory=dataclass_field_required('values'))

    # map_range returns MapNodeIter instance.
    def map_range(self) -> MapYamlNodeIter:
        ret = MapYamlNodeIter(values=[], idx=YAML_START_RANGE_INDEX)
        for value in self.values:
            it = value.map_range()
            ret.values.extend(it.values)
        return ret


##


# AnchorNode type of anchor node
@dc.dataclass()
class AnchorYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    name: ta.Optional[YamlNode] = None
    value: ta.Optional[YamlNode] = None

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    def set_name(self, name: str) -> ta.Optional[YamlError]:
        if self.name is None:
            return YamlAstErrors.INVALID_ANCHOR_NAME
        s = self.name
        if not isinstance(s, StringYamlNode):
            return YamlAstErrors.INVALID_ANCHOR_NAME
        s.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns AnchorType
    def type(self) -> YamlNodeType:
        return YamlNodeType.ANCHOR

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    def get_value(self) -> ta.Any:
        return check.not_none(check.not_none(self.value).get_token()).value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.name is not None:
            self.name.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # String anchor to text
    def string(self) -> str:
        anchor = '&' + check.not_none(self.name).string()
        value = check.not_none(self.value).string()
        if isinstance(self.value, SequenceYamlNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        elif isinstance(self.value, MappingYamlNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        if value == '':
            # implicit null value.
            return anchor
        return f'{anchor} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()


##


# AliasNode type of alias node
@dc.dataclass()
class AliasYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    def set_name(self, name: str) -> ta.Optional[YamlError]:
        if self.value is None:
            return YamlAstErrors.INVALID_ALIAS_NAME
        if not isinstance(self.value, StringYamlNode):
            return YamlAstErrors.INVALID_ALIAS_NAME
        self.value.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns AliasType
    def type(self) -> YamlNodeType:
        return YamlNodeType.ALIAS

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    def get_value(self) -> ta.Any:
        return check.not_none(check.not_none(self.value).get_token()).value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String alias to text
    def string(self) -> str:
        return f'*{check.not_none(self.value).string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# DirectiveNode type of directive node
@dc.dataclass()
class DirectiveYamlNode(BaseYamlNode):
    # Start is '%' token.
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    # Name is directive name e.g.) "YAML" or "TAG".
    name: ta.Optional[YamlNode] = None
    # Values is directive values e.g.) "1.2" or "!!" and "tag:clarkevans.com,2002:app/".
    values: ta.List[YamlNode] = dc.field(default_factory=list)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns DirectiveType
    def type(self) -> YamlNodeType:
        return YamlNodeType.DIRECTIVE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.name is not None:
            self.name.add_column(col)
        for value in self.values:
            value.add_column(col)

    # String directive to text
    def string(self) -> str:
        values: ta.List[str] = []
        for val in self.values:
            values.append(val.string())
        return ' '.join(['%' + check.not_none(self.name).string(), *values])

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# TagNode type of tag node
@dc.dataclass()
class TagYamlNode(ScalarYamlNode, BaseYamlNode, ArrayYamlNode):
    directive: ta.Optional[DirectiveYamlNode] = None
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    def get_value(self) -> ta.Any:
        if not isinstance(self.value, ScalarYamlNode):
            return None
        return self.value.get_value()

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns TagType
    def type(self) -> YamlNodeType:
        return YamlNodeType.TAG

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def string(self) -> str:
        value = check.not_none(self.value).string()
        if isinstance(self.value, SequenceYamlNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'
        elif isinstance(self.value, MappingYamlNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'

        return f'{self.start.value} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()

    def array_range(self) -> ta.Optional[ArrayYamlNodeIter]:
        arr = self.value
        if not isinstance(arr, ArrayYamlNode):
            return None
        return arr.array_range()


##


# CommentNode type of comment node
@dc.dataclass()
class CommentYamlNode(BaseYamlNode):
    token: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns CommentType
    def type(self) -> YamlNodeType:
        return YamlNodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # String comment to text
    def string(self) -> str:
        return f'#{check.not_none(self.token).value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# CommentGroupNode type of comment node
@dc.dataclass()
class CommentGroupYamlNode(BaseYamlNode):
    comments: ta.List[CommentYamlNode] = dc.field(default_factory=dataclass_field_required('comments'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns CommentType
    def type(self) -> YamlNodeType:
        return YamlNodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        if len(self.comments) > 0:
            return self.comments[0].token
        return None

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        for comment in self.comments:
            comment.add_column(col)

    # String comment to text
    def string(self) -> str:
        values: ta.List[str] = []
        for comment in self.comments:
            values.append(comment.string())
        return '\n'.join(values)

    def string_with_space(self, col: int) -> str:
        values: ta.List[str] = []
        space = ' ' * col
        for comment in self.comments:
            spc = space
            if yaml_check_line_break(check.not_none(comment.token)):
                spc = f'\n{spc}'
            values.append(spc + comment.string())
        return '\n'.join(values)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# Visitor has Visit method that is invokded for each node encountered by walk.
# If the result visitor w is not nil, walk visits each of the children of node with the visitor w,
# followed by a call of w.visit(nil).
class YamlAstVisitor(Abstract):
    @abc.abstractmethod
    def visit(self, node: YamlNode) -> ta.Optional['YamlAstVisitor']:
        raise NotImplementedError


# walk traverses an AST in depth-first order: It starts by calling v.visit(node); node must not be nil.
# If the visitor w returned by v.visit(node) is not nil,
# walk is invoked recursively with visitor w for each of the non-nil children of node,
# followed by a call of w.visit(nil).
def yaml_ast_walk(v: YamlAstVisitor, node: YamlNode) -> None:
    if (v_ := v.visit(node)) is None:
        return
    v = v_

    n = node
    if isinstance(n, (CommentYamlNode, NullYamlNode)):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, IntegerYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, FloatYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, StringYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, MergeKeyYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, BoolYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, InfinityYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, NanYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, LiteralYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, DirectiveYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.name))
        for value0 in n.values:
            yaml_ast_walk(v, value0)
    if isinstance(n, TagYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, DocumentYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.body))
    if isinstance(n, MappingYamlNode):
        yaml_ast_walk_comment(v, n)
        for value1 in n.values:
            yaml_ast_walk(v, value1)
    if isinstance(n, MappingKeyYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, MappingValueYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, n.key)
        yaml_ast_walk(v, n.value)
    if isinstance(n, SequenceYamlNode):
        yaml_ast_walk_comment(v, n)
        for value2 in n.values:
            yaml_ast_walk(v, check.not_none(value2))
    if isinstance(n, AnchorYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.name))
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, AliasYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))


def yaml_ast_walk_comment(v: YamlAstVisitor, base: ta.Optional[BaseYamlNode]) -> None:
    if base is None:
        return
    if base.comment is None:
        return
    yaml_ast_walk(v, base.comment)


#


@dc.dataclass()
class FilterYamlAstWalker(YamlAstVisitor):
    typ: YamlNodeType = dc.field(default_factory=dataclass_field_required('typ'))
    results: ta.List[YamlNode] = dc.field(default_factory=list)

    def visit(self, n: YamlNode) -> YamlAstVisitor:
        if self.typ == n.type():
            self.results.append(n)
        return self


#


@dc.dataclass()
class YamlParentFinder:
    target: YamlNode

    def walk(self, parent: YamlNode, node: ta.Optional[YamlNode]) -> ta.Optional[YamlNode]:
        if self.target == node:
            return parent

        n = node
        if isinstance(n, CommentYamlNode):
            return None
        if isinstance(n, NullYamlNode):
            return None
        if isinstance(n, IntegerYamlNode):
            return None
        if isinstance(n, FloatYamlNode):
            return None
        if isinstance(n, StringYamlNode):
            return None
        if isinstance(n, MergeKeyYamlNode):
            return None
        if isinstance(n, BoolYamlNode):
            return None
        if isinstance(n, InfinityYamlNode):
            return None
        if isinstance(n, NanYamlNode):
            return None
        if isinstance(n, LiteralYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, DirectiveYamlNode):
            if (found := self.walk(n, n.name)) is not None:
                return found
            for value0 in n.values:
                if (found := self.walk(n, value0)) is not None:
                    return found
        if isinstance(n, TagYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, DocumentYamlNode):
            return self.walk(n, n.body)
        if isinstance(n, MappingYamlNode):
            for value1 in n.values:
                if (found := self.walk(n, value1)) is not None:
                    return found
        if isinstance(n, MappingKeyYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, MappingValueYamlNode):
            if (found := self.walk(n, n.key)) is not None:
                return found
            return self.walk(n, n.value)
        if isinstance(n, SequenceYamlNode):
            for value2 in n.values:
                if (found := self.walk(n, value2)) is not None:
                    return found
        if isinstance(n, AnchorYamlNode):
            if (found := self.walk(n, n.name)) is not None:
                return found
            return self.walk(n, n.value)
        if isinstance(n, AliasYamlNode):
            return self.walk(n, n.value)
        return None


# Parent get parent node from child node.
def yaml_parent(root: YamlNode, child: YamlNode) -> ta.Optional[YamlNode]:
    finder = YamlParentFinder(target=child)
    return finder.walk(root, root)


#


# Filter returns a list of nodes that match the given type.
def yaml_filter(typ: YamlNodeType, node: YamlNode) -> ta.List[YamlNode]:
    walker = FilterYamlAstWalker(typ=typ)
    yaml_ast_walk(walker, node)
    return walker.results


# FilterFile returns a list of nodes that match the given type.
def yaml_filter_file(typ: YamlNodeType, file: YamlFile) -> ta.List[YamlNode]:
    results: ta.List[YamlNode] = []
    for doc in file.docs:
        walker = FilterYamlAstWalker(typ=typ)
        yaml_ast_walk(walker, doc)
        results.extend(walker.results)
    return results


#


@dc.dataclass()
class InvalidMergeTypeYamlError(YamlError):
    dst: YamlNode
    src: YamlNode

    @property
    def message(self) -> str:
        return f'cannot merge {self.src.type()} into {self.dst.type()}'


# Merge merge document, map, sequence node.
def yaml_ast_merge(dst: YamlNode, src: YamlNode) -> ta.Optional[YamlError]:
    if isinstance(src, DocumentYamlNode):
        doc: DocumentYamlNode = src
        src = check.not_none(doc.body)

    err = InvalidMergeTypeYamlError(dst=dst, src=src)
    if dst.type() == YamlNodeType.DOCUMENT:
        node0: DocumentYamlNode = check.isinstance(dst, DocumentYamlNode)
        return yaml_ast_merge(check.not_none(node0.body), src)
    if dst.type() == YamlNodeType.MAPPING:
        node1: MappingYamlNode = check.isinstance(dst, MappingYamlNode)
        if not isinstance(src, MappingYamlNode):
            return err
        target0: MappingYamlNode = src
        node1.merge(target0)
        return None
    if dst.type() == YamlNodeType.SEQUENCE:
        node2: SequenceYamlNode = check.isinstance(dst, SequenceYamlNode)
        if not isinstance(src, SequenceYamlNode):
            return err
        target1: SequenceYamlNode = src
        node2.merge(target1)
        return None
    return err


########################################
# ../scanning.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


@dc.dataclass()
class InvalidTokenYamlError(YamlError):
    token: YamlToken

    @property
    def message(self) -> str:
        return check.not_none(self.token.error).message


def _yaml_err_invalid_token(tk: YamlToken) -> InvalidTokenYamlError:
    return InvalidTokenYamlError(
        token=tk,
    )


##


# Context at scanning
@dc.dataclass()
class YamlScanningContext:
    idx: int = 0
    size: int = 0
    not_space_char_pos: int = 0
    not_space_org_char_pos: int = 0
    src: ta.List[str] = dc.field(default_factory=list)
    buf: ta.List[str] = dc.field(default_factory=list)
    obuf: ta.List[str] = dc.field(default_factory=list)
    tokens: YamlTokens = dc.field(default_factory=YamlTokens)
    mstate: ta.Optional['YamlMultiLineState'] = None

    def clear(self) -> None:
        self.reset_buffer()
        self.mstate = None

    def reset(self, src: ta.List[str]) -> None:
        self.idx = 0
        self.size = len(src)
        self.src = list(src)
        self.tokens = YamlTokens()
        self.reset_buffer()
        self.mstate = None

    def reset_buffer(self) -> None:
        self.buf = []
        self.obuf = []
        self.not_space_char_pos = 0
        self.not_space_org_char_pos = 0

    def break_multi_line(self) -> None:
        self.mstate = None

    def get_multi_line_state(self) -> ta.Optional['YamlMultiLineState']:
        return self.mstate

    def set_literal(self, last_delim_column: int, opt: str) -> None:
        mstate = YamlMultiLineState(
            is_literal=True,
            opt=opt,
        )
        indent = _yaml_first_line_indent_column_by_opt(opt)
        if indent > 0:
            mstate.first_line_indent_column = last_delim_column + indent
        self.mstate = mstate

    def set_folded(self, last_delim_column: int, opt: str) -> None:
        mstate = YamlMultiLineState(
            is_folded=True,
            opt=opt,
        )
        indent = _yaml_first_line_indent_column_by_opt(opt)
        if indent > 0:
            mstate.first_line_indent_column = last_delim_column + indent
        self.mstate = mstate

    def set_raw_folded(self, column: int) -> None:
        mstate = YamlMultiLineState(
            is_raw_folded=True,
        )
        mstate.update_indent_column(column)
        self.mstate = mstate

    def add_token(self, tk: ta.Optional[YamlToken]) -> None:
        if tk is None:
            return
        self.tokens.append(tk)  # FIXME: .add??

    def add_buf(self, r: str) -> None:
        if len(self.buf) == 0 and (r == ' ' or r == '\t'):
            return
        self.buf += r
        if r != ' ' and r != '\t':
            self.not_space_char_pos = len(self.buf)

    def add_buf_with_tab(self, r: str) -> None:
        if len(self.buf) == 0 and r == ' ':
            return
        self.buf += r
        if r != ' ':
            self.not_space_char_pos = len(self.buf)

    def add_origin_buf(self, r: str) -> None:
        self.obuf += r
        if r != ' ' and r != '\t':
            self.not_space_org_char_pos = len(self.obuf)

    def remove_right_space_from_buf(self) -> None:
        trimmed_buf = self.obuf[:self.not_space_org_char_pos]
        buflen = len(trimmed_buf)
        diff = len(self.obuf) - buflen
        if diff > 0:
            self.obuf = self.obuf[:buflen]
            self.buf = list(self.buffered_src())

    def is_eos(self) -> bool:
        return len(self.src) - 1 <= self.idx

    def is_next_eos(self) -> bool:
        return len(self.src) <= self.idx + 1

    def next(self) -> bool:
        return self.idx < self.size

    def source(self, s: int, e: int) -> str:
        return ''.join(self.src[s:e])

    def previous_char(self) -> str:
        if self.idx > 0:
            return self.src[self.idx - 1]
        return ''

    def current_char(self) -> str:
        if self.size > self.idx:
            return self.src[self.idx]
        return ''

    def next_char(self) -> str:
        if self.size > self.idx + 1:
            return self.src[self.idx + 1]
        return ''

    def repeat_num(self, r: str) -> int:
        cnt = 0
        for i in range(self.idx, self.size):
            if self.src[i] == r:
                cnt += 1
            else:
                break
        return cnt

    def progress(self, num: int) -> None:
        self.idx += num

    def exists_buffer(self) -> bool:
        return len(self.buffered_src()) != 0

    def is_multi_line(self) -> bool:
        return self.mstate is not None

    def buffered_src(self) -> ta.List[str]:
        src = self.buf[:self.not_space_char_pos]

        if self.is_multi_line():
            mstate = check.not_none(self.get_multi_line_state())

            # remove end '\n' character and trailing empty lines.
            # https://yaml.org/spec/1.2.2/#8112-block-chomping-indicator
            if mstate.has_trim_all_end_newline_opt():
                # If the '-' flag is specified, all trailing newline characters will be removed.
                src = list(''.join(src).rstrip('\n'))

            elif not mstate.has_keep_all_end_newline_opt():
                # Normally, all but one of the trailing newline characters are removed.
                new_line_char_count = 0
                for i in range(len(src) - 1, -1, -1):
                    if src[i] == '\n':
                        new_line_char_count += 1
                        continue
                    break

                removed_new_line_char_count = new_line_char_count - 1
                while removed_new_line_char_count > 0:
                    src = list(''.join(src).rstrip('\n'))
                    removed_new_line_char_count -= 1

            # If the text ends with a space character, remove all of them.
            if mstate.has_trim_all_end_newline_opt():
                src = list(''.join(src).rstrip(' '))

            if src == ['\n']:
                # If the content consists only of a newline, it can be considered as the document ending without any
                # specified value, so it is treated as an empty string.
                src = []

            if mstate.has_keep_all_end_newline_opt() and len(src) == 0:
                src = ['\n']

        return src

    def buffered_token(self, pos: YamlPosition) -> ta.Optional[YamlToken]:
        if self.idx == 0:
            return None

        source = self.buffered_src()
        if len(source) == 0:
            self.buf = self.buf[:0]  # clear value's buffer only.
            return None

        tk: ta.Optional[YamlToken]
        if self.is_multi_line():
            tk = YamlTokenMakers.new_string(''.join(source), ''.join(self.obuf), pos)
        else:
            tk = yaml_new_token(''.join(source), ''.join(self.obuf), pos)

        self.set_token_type_by_prev_tag(tk)
        self.reset_buffer()
        return tk

    def set_token_type_by_prev_tag(self, tk: ta.Optional[YamlToken]) -> None:
        last_tk = self.last_token()
        if last_tk is None:
            return

        if last_tk.type != YamlTokenType.TAG:
            return

        tag = last_tk.value
        if tag not in YAML_RESERVED_TAG_KEYWORD_MAP:
            check.not_none(tk).type = YamlTokenType.STRING

    def last_token(self) -> ta.Optional[YamlToken]:
        if len(self.tokens) != 0:
            return self.tokens[-1]

        return None

    @staticmethod
    def new(src: ta.List[str]) -> 'YamlScanningContext':
        ctx = YamlScanningContext()
        ctx.reset(src)
        return ctx


##


@dc.dataclass()
class YamlMultiLineState:
    opt: str = ''
    first_line_indent_column: int = 0
    prev_line_indent_column: int = 0
    line_indent_column: int = 0
    last_not_space_only_line_indent_column: int = 0
    space_only_indent_column: int = 0
    folded_new_line: bool = False
    is_raw_folded: bool = False
    is_literal: bool = False
    is_folded: bool = False

    def last_delim_column(self) -> int:
        if self.first_line_indent_column == 0:
            return 0
        return self.first_line_indent_column - 1

    def update_indent_column(self, column: int) -> None:
        if self.first_line_indent_column == 0:
            self.first_line_indent_column = column
        if self.line_indent_column == 0:
            self.line_indent_column = column

    def update_space_only_indent_column(self, column: int) -> None:
        if self.first_line_indent_column != 0:
            return
        self.space_only_indent_column = column

    def validate_indent_after_space_only(self, column: int) -> ta.Optional[YamlError]:
        if self.first_line_indent_column != 0:
            return None
        if self.space_only_indent_column > column:
            return yaml_error('invalid number of indent is specified after space only')
        return None

    def validate_indent_column(self) -> ta.Optional[YamlError]:
        if _yaml_first_line_indent_column_by_opt(self.opt) == 0:
            return None
        if self.first_line_indent_column > self.line_indent_column:
            return yaml_error('invalid number of indent is specified in the multi-line header')
        return None

    def update_new_line_state(self) -> None:
        self.prev_line_indent_column = self.line_indent_column
        if self.line_indent_column != 0:
            self.last_not_space_only_line_indent_column = self.line_indent_column
        self.folded_new_line = True
        self.line_indent_column = 0

    def is_indent_column(self, column: int) -> bool:
        if self.first_line_indent_column == 0:
            return column == 1
        return self.first_line_indent_column > column

    def add_indent(self, ctx: YamlScanningContext, column: int) -> None:
        if self.first_line_indent_column == 0:
            return

        # If the first line of the document has already been evaluated, the number is treated as the threshold, since
        # the `first_line_indent_column` is a positive number.
        if column < self.first_line_indent_column:
            return

        # `c.folded_new_line` is a variable that is set to True for every newline.
        if not self.is_literal and self.folded_new_line:
            self.folded_new_line = False

        # Since add_buf ignore space character, add to the buffer directly.
        ctx.buf += ' '
        ctx.not_space_char_pos = len(ctx.buf)

    # update_new_line_in_folded if Folded or RawFolded context and the content on the current line starts at the same
    # column as the previous line, treat the new-line-char as a space.
    def update_new_line_in_folded(self, ctx: YamlScanningContext, column: int) -> None:
        if self.is_literal:
            return

        # Folded or RawFolded.

        if not self.folded_new_line:
            return

        last_char = ''
        prev_last_char = ''
        if len(ctx.buf) != 0:
            last_char = ctx.buf[-1]
        if len(ctx.buf) > 1:
            prev_last_char = ctx.buf[-2]

        if self.line_indent_column == self.prev_line_indent_column:
            # ---
            # >
            #  a
            #  b
            if last_char == '\n':
                ctx.buf[-1] = ' '

        elif self.prev_line_indent_column == 0 and self.last_not_space_only_line_indent_column == column:
            # if previous line is indent-space and new-line-char only, prev_line_indent_column is zero. In this case,
            # last new-line-char is removed.
            # ---
            # >
            #  a
            #
            #  b
            if last_char == '\n' and prev_last_char == '\n':
                ctx.buf = ctx.buf[:len(ctx.buf) - 1]
                ctx.not_space_char_pos = len(ctx.buf)

        self.folded_new_line = False

    def has_trim_all_end_newline_opt(self) -> bool:
        return self.opt.startswith('-') or self.opt.endswith('-') or self.is_raw_folded

    def has_keep_all_end_newline_opt(self) -> bool:
        return self.opt.startswith('+') or self.opt.endswith('+')


##


def _yaml_first_line_indent_column_by_opt(opt: str) -> int:
    opt = opt.lstrip('-')
    opt = opt.lstrip('+')
    opt = opt.rstrip('-')
    opt = opt.rstrip('+')
    try:
        return int(opt, 10)
    except ValueError:
        return 0


##


class YamlIndentState(enum.Enum):
    # EQUAL equals previous indent
    EQUAL = enum.auto()
    # UP more indent than previous
    UP = enum.auto()
    # DOWN less indent than previous
    DOWN = enum.auto()
    # KEEP uses not indent token
    KEEP = enum.auto()


# Scanner holds the scanner's internal state while processing a given text. It can be allocated as part of another data
# structure but must be initialized via init before use.
@dc.dataclass()
class YamlScanner:
    source: ta.List[str] = dc.field(default_factory=list)
    source_pos: int = 0
    source_size: int = 0
    # line number. This number starts from 1.
    line: int = 0
    # column number. This number starts from 1.
    column: int = 0
    # offset represents the offset from the beginning of the source.
    offset: int = 0
    # last_delim_column is the last column needed to compare indent is retained.
    last_delim_column: int = 0
    # indent_num indicates the number of spaces used for indentation.
    indent_num: int = 0
    # prev_line_indent_num indicates the number of spaces used for indentation at previous line.
    prev_line_indent_num: int = 0
    # indent_level indicates the level of indent depth. This value does not match the column value.
    indent_level: int = 0
    is_first_char_at_line: bool = False
    is_anchor: bool = False
    is_alias: bool = False
    is_directive: bool = False
    started_flow_sequence_num: int = 0
    started_flow_map_num: int = 0
    indent_state: YamlIndentState = YamlIndentState.EQUAL
    saved_pos: ta.Optional[YamlPosition] = None

    def pos(self) -> YamlPosition:
        return YamlPosition(
            line=self.line,
            column=self.column,
            offset=self.offset,
            indent_num=self.indent_num,
            indent_level=self.indent_level,
        )

    def buffered_token(self, ctx: YamlScanningContext) -> ta.Optional[YamlToken]:
        if self.saved_pos is not None:
            tk = ctx.buffered_token(self.saved_pos)
            self.saved_pos = None
            return tk

        line = self.line
        column = self.column - len(ctx.buf)
        level = self.indent_level
        if ctx.is_multi_line():
            line -= self.new_line_count(ctx.buf)
            column = ''.join(ctx.obuf).find(''.join(ctx.buf)) + 1
            # Since we are in a literal, folded or raw folded we can use the indent level from the last token.
            last = ctx.last_token()
            if last is not None:  # The last token should never be None here.
                level = last.position.indent_level + 1

        return ctx.buffered_token(YamlPosition(
            line=line,
            column=column,
            offset=self.offset - len(ctx.buf),
            indent_num=self.indent_num,
            indent_level=level,
        ))

    def progress_column(self, ctx: YamlScanningContext, num: int) -> None:
        self.column += num
        self.offset += num
        self.progress(ctx, num)

    def progress_only(self, ctx: YamlScanningContext, num: int) -> None:
        self.offset += num
        self.progress(ctx, num)

    def progress_line(self, ctx: YamlScanningContext) -> None:
        self.prev_line_indent_num = self.indent_num
        self.column = 1
        self.line += 1
        self.offset += 1
        self.indent_num = 0
        self.is_first_char_at_line = True
        self.is_anchor = False
        self.is_alias = False
        self.is_directive = False
        self.progress(ctx, 1)

    def progress(self, ctx: YamlScanningContext, num: int) -> None:
        ctx.progress(num)
        self.source_pos += num

    def is_new_line_char(self, c: str) -> bool:
        if c == '\n':
            return True
        if c == '\r':
            return True
        return False

    def new_line_count(self, src: ta.List[str]) -> int:
        size = len(src)
        cnt = 0
        i = -1
        while True:
            i += 1
            if not (i < size):
                break
            c = src[i]
            if c == '\r':
                if i + 1 < size and src[i + 1] == '\n':
                    i += 1
                cnt += 1
            elif c == '\n':
                cnt += 1
        return cnt

    def update_indent_level(self) -> None:
        if self.prev_line_indent_num < self.indent_num:
            self.indent_level += 1
        elif self.prev_line_indent_num > self.indent_num:
            if self.indent_level > 0:
                self.indent_level -= 1

    def update_indent_state(self, ctx: YamlScanningContext) -> None:
        if self.last_delim_column == 0:
            return

        if self.last_delim_column < self.column:
            self.indent_state = YamlIndentState.UP
        else:
            # If last_delim_column and self.column are the same, treat as Down state since it is the same column as
            # delimiter.
            self.indent_state = YamlIndentState.DOWN

    def update_indent(self, ctx: YamlScanningContext, c: str) -> None:
        if self.is_first_char_at_line and self.is_new_line_char(c):
            return
        if self.is_first_char_at_line and c == ' ':
            self.indent_num += 1
            return
        if self.is_first_char_at_line and c == '\t':
            # Found tab indent. In this case, scan_tab returns error.
            return
        if not self.is_first_char_at_line:
            self.indent_state = YamlIndentState.KEEP
            return
        self.update_indent_level()
        self.update_indent_state(ctx)
        self.is_first_char_at_line = False

    def is_changed_to_indent_state_down(self) -> bool:
        return self.indent_state == YamlIndentState.DOWN

    def is_changed_to_indent_state_up(self) -> bool:
        return self.indent_state == YamlIndentState.UP

    def add_buffered_token_if_exists(self, ctx: YamlScanningContext) -> None:
        ctx.add_token(self.buffered_token(ctx))

    def break_multi_line(self, ctx: YamlScanningContext) -> None:
        ctx.break_multi_line()

    def scan_single_quote(self, ctx: YamlScanningContext) -> YamlErrorOr[YamlToken]:
        ctx.add_origin_buf("'")
        srcpos = self.pos()
        start_index = ctx.idx + 1
        src = ctx.src
        size = len(src)
        value: ta.List[str] = []
        is_first_line_char = False
        is_new_line = False

        idx = start_index - 1
        while True:
            idx += 1
            if not (idx < size):
                break

            if not is_new_line:
                self.progress_column(ctx, 1)
            else:
                is_new_line = False

            c = src[idx]
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                not_space_idx = -1
                for i in range(len(value) - 1, -1, -1):
                    if value[i] == ' ':
                        continue
                    not_space_idx = i
                    break

                if len(value) > not_space_idx:
                    value = value[:not_space_idx + 1]
                if is_first_line_char:
                    value += '\n'
                else:
                    value += ' '

                is_first_line_char = True
                is_new_line = True
                self.progress_line(ctx)
                if idx + 1 < size:
                    if (err := self.validate_document_separator_marker(ctx, src[idx + 1:])) is not None:
                        return err

                continue

            if is_first_line_char and c == ' ':
                continue

            if is_first_line_char and c == '\t':
                if self.last_delim_column >= self.column:
                    return _yaml_err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error('tab character cannot be used for indentation in single-quoted text'),
                            ''.join(ctx.obuf),
                            self.pos(),
                        ),
                    )

                continue

            if c != "'":
                value += c
                is_first_line_char = False
                continue

            if idx + 1 < len(ctx.src) and ctx.src[idx + 1] == '\'':
                # '' handle as ' character
                value += c
                ctx.add_origin_buf(c)
                idx += 1
                self.progress_column(ctx, 1)
                continue

            self.progress_column(ctx, 1)
            return YamlTokenMakers.new_single_quote(''.join(value), ''.join(ctx.obuf), srcpos)

        self.progress_column(ctx, 1)
        return _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error('could not find end character of single-quoted text'),
                ''.join(ctx.obuf),
                srcpos,
            ),
        )

    def scan_double_quote(self, ctx: YamlScanningContext) -> YamlErrorOr[YamlToken]:
        ctx.add_origin_buf('"')
        srcpos = self.pos()
        start_index = ctx.idx + 1
        src = ctx.src
        size = len(src)
        value: ta.List[str] = []
        is_first_line_char = False
        is_new_line = False

        idx = start_index - 1
        while True:
            idx += 1
            if not (idx < size):
                break

            if not is_new_line:
                self.progress_column(ctx, 1)
            else:
                is_new_line = False

            c = src[idx]
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                not_space_idx = -1
                for i in range(len(value) - 1, -1, -1):
                    if value[i] == ' ':
                        continue
                    not_space_idx = i
                    break

                if len(value) > not_space_idx:
                    value = value[:not_space_idx + 1]

                if is_first_line_char:
                    value += '\n'
                else:
                    value += ' '

                is_first_line_char = True
                is_new_line = True
                self.progress_line(ctx)
                if idx + 1 < size:
                    if (err := self.validate_document_separator_marker(ctx, src[idx + 1:])) is not None:
                        return err

                continue

            if is_first_line_char and c == ' ':
                continue

            if is_first_line_char and c == '\t':
                if self.last_delim_column >= self.column:
                    return _yaml_err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error('tab character cannot be used for indentation in double-quoted text'),
                            ''.join(ctx.obuf),
                            self.pos(),
                        ),
                    )

                continue

            if c == '\\':
                is_first_line_char = False
                if idx + 1 >= size:
                    value += c
                    continue

                next_char = src[idx + 1]
                progress = 0

                if next_char == '0':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += chr(0)
                elif next_char == 'a':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x07'
                elif next_char == 'b':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x08'
                elif next_char == 't':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x09'
                elif next_char == 'n':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0A'
                elif next_char == 'v':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0B'
                elif next_char == 'f':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0C'
                elif next_char == 'r':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0D'
                elif next_char == 'e':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x1B'
                elif next_char == ' ':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x20'
                elif next_char == '"':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x22'
                elif next_char == '/':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x2F'
                elif next_char == '\\':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x5C'
                elif next_char == 'N':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x85'
                elif next_char == '_':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\xA0'
                elif next_char == 'L':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\u2028'
                elif next_char == 'P':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\u2029'

                elif next_char == 'x':
                    if idx + 3 >= size:
                        progress = 1
                        ctx.add_origin_buf(next_char)
                        value += next_char
                    else:
                        progress = 3
                        code_num = _yaml_hex_runes_to_int(src[idx + 2: idx + progress + 1])
                        value += chr(code_num)

                elif next_char == 'u':
                    # \u0000 style must have 5 characters at least.
                    if idx + 5 >= size:
                        return _yaml_err_invalid_token(
                            YamlTokenMakers.new_invalid(
                                yaml_error('not enough length for escaped UTF-16 character'),
                                ''.join(ctx.obuf),
                                self.pos(),
                            ),
                        )

                    progress = 5
                    code_num = _yaml_hex_runes_to_int(src[idx + 2: idx + 6])

                    # handle surrogate pairs.
                    if code_num >= 0xD800 and code_num <= 0xDBFF:
                        high = code_num

                        # \u0000\u0000 style must have 11 characters at least.
                        if idx + 11 >= size:
                            return _yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('not enough length for escaped UTF-16 surrogate pair'),
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            )

                        if src[idx + 6] != '\\' or src[idx + 7] != 'u':
                            return _yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('found unexpected character after high surrogate for UTF-16 surrogate pair'),  # noqa
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            )

                        low = _yaml_hex_runes_to_int(src[idx + 8: idx + 12])
                        if low < 0xDC00 or low > 0xDFFF:
                            return _yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('found unexpected low surrogate after high surrogate'),
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            )

                        code_num = ((high - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000
                        progress += 6

                    value += chr(code_num)

                elif next_char == 'U':
                    # \U00000000 style must have 9 characters at least.
                    if idx + 9 >= size:
                        return _yaml_err_invalid_token(
                            YamlTokenMakers.new_invalid(
                                yaml_error('not enough length for escaped UTF-32 character'),
                                ''.join(ctx.obuf),
                                self.pos(),
                            ),
                        )

                    progress = 9
                    code_num = _yaml_hex_runes_to_int(src[idx + 2: idx + 10])
                    value += chr(code_num)

                elif next_char == '\n':
                    is_first_line_char = True
                    is_new_line = True
                    ctx.add_origin_buf(next_char)
                    self.progress_column(ctx, 1)
                    self.progress_line(ctx)
                    idx += 1
                    continue

                elif next_char == '\r':
                    is_first_line_char = True
                    is_new_line = True
                    ctx.add_origin_buf(next_char)
                    self.progress_line(ctx)
                    progress = 1
                    # Skip \n after \r in CRLF sequences
                    if idx + 2 < size and src[idx + 2] == '\n':
                        ctx.add_origin_buf('\n')
                        progress = 2

                elif next_char == '\t':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += next_char

                else:
                    self.progress_column(ctx, 1)
                    return _yaml_err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error(f'found unknown escape character {next_char!r}'),
                            ''.join(ctx.obuf),
                            self.pos(),
                        ),
                    )

                idx += progress
                self.progress_column(ctx, progress)
                continue

            if c == '\t':
                found_not_space_char = False
                progress = 0

                for i in range(idx + 1, size):
                    if src[i] == ' ' or src[i] == '\t':
                        progress += 1
                        continue

                    if self.is_new_line_char(src[i]):
                        break

                    found_not_space_char = True

                if found_not_space_char:
                    value += c
                    if src[idx + 1] != '"':
                        self.progress_column(ctx, 1)

                else:
                    idx += progress
                    self.progress_column(ctx, progress)

                continue

            if c != '"':
                value += c
                is_first_line_char = False
                continue

            self.progress_column(ctx, 1)
            return YamlTokenMakers.new_double_quote(''.join(value), ''.join(ctx.obuf), srcpos)

        self.progress_column(ctx, 1)
        return _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error('could not find end character of double-quoted text'),
                ''.join(ctx.obuf),
                srcpos,
            ),
        )

    def validate_document_separator_marker(self, ctx: YamlScanningContext, src: ta.List[str]) -> ta.Optional[YamlError]:
        if self.found_document_separator_marker(src):
            return _yaml_err_invalid_token(
                YamlTokenMakers.new_invalid(
                    yaml_error('found unexpected document separator'),
                    ''.join(ctx.obuf),
                    self.pos(),
                ),
            )

        return None

    def found_document_separator_marker(self, src: ta.List[str]) -> bool:
        if len(src) < 3:
            return False

        marker = ''
        if len(src) == 3:
            marker = ''.join(src)
        else:
            marker = _yaml_trim_right_func(''.join(src[:4]), lambda r: r == ' ' or r == '\t' or r == '\n' or r == '\r')

        return marker == '---' or marker == '...'

    def scan_quote(self, ctx: YamlScanningContext, ch: str) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        if ch == "'":
            tk = self.scan_single_quote(ctx)
            if isinstance(tk, YamlError):
                return tk

            ctx.add_token(tk)

        else:
            tk = self.scan_double_quote(ctx)
            if isinstance(tk, YamlError):
                return tk

            ctx.add_token(tk)

        ctx.clear()
        return True

    def scan_white_space(self, ctx: YamlScanningContext) -> bool:
        if ctx.is_multi_line():
            return False

        if not self.is_anchor and not self.is_directive and not self.is_alias and not self.is_first_char_at_line:
            return False

        if self.is_first_char_at_line:
            self.progress_column(ctx, 1)
            ctx.add_origin_buf(' ')
            return True

        if self.is_directive:
            self.add_buffered_token_if_exists(ctx)
            self.progress_column(ctx, 1)
            ctx.add_origin_buf(' ')
            return True

        self.add_buffered_token_if_exists(ctx)
        self.is_anchor = False
        self.is_alias = False
        return True

    def is_merge_key(self, ctx: YamlScanningContext) -> bool:
        if ctx.repeat_num('<') != 2:
            return False

        src = ctx.src
        size = len(src)
        for idx in range(ctx.idx + 2, size):
            c = src[idx]
            if c == ' ':
                continue

            if c != ':':
                return False

            if idx + 1 < size:
                nc = src[idx + 1]
                if nc == ' ' or self.is_new_line_char(nc):
                    return True

        return False

    def scan_tag(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer() or self.is_directive:
            return False

        ctx.add_origin_buf('!')
        self.progress(ctx, 1)  # skip '!' character

        progress = 0
        for idx, c in enumerate(ctx.src[ctx.idx:]):
            progress = idx + 1

            if c == ' ':
                ctx.add_origin_buf(c)
                value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                ctx.add_token(YamlTokenMakers.new_tag(value, ''.join(ctx.obuf), self.pos()))
                self.progress_column(ctx, len(value))
                ctx.clear()
                return True

            elif c == ',':
                if self.started_flow_sequence_num > 0 or self.started_flow_map_num > 0:
                    value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                    ctx.add_token(YamlTokenMakers.new_tag(value, ''.join(ctx.obuf), self.pos()))
                    # progress column before collect-entry for scanning it at scan_flow_entry function.
                    self.progress_column(ctx, len(value) - 1)
                    ctx.clear()
                    return True
                else:
                    ctx.add_origin_buf(c)

            elif c in ('\n', '\r'):
                ctx.add_origin_buf(c)
                value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                ctx.add_token(YamlTokenMakers.new_tag(value, ''.join(ctx.obuf), self.pos()))
                # progress column before new-line-char for scanning new-line-char at scan_new_line function.
                self.progress_column(ctx, len(value) - 1)
                ctx.clear()
                return True

            elif c in ('{', '}'):
                ctx.add_origin_buf(c)
                self.progress_column(ctx, progress)
                invalid_tk = YamlTokenMakers.new_invalid(
                    yaml_error(f'found invalid tag character {c!r}'),
                    ''.join(ctx.obuf),
                    self.pos(),
                )
                return _yaml_err_invalid_token(invalid_tk)

            else:
                ctx.add_origin_buf(c)

        self.progress_column(ctx, progress)
        ctx.clear()
        return True

    def scan_comment(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            c = ctx.previous_char()
            if c != ' ' and c != '\t' and not self.is_new_line_char(c):
                return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('#')
        self.progress(ctx, 1)  # skip '#' character

        for idx, c in enumerate(ctx.src[ctx.idx:]):
            ctx.add_origin_buf(c)
            if not self.is_new_line_char(c):
                continue
            if ctx.previous_char() == '\\':
                continue

            value = ctx.source(ctx.idx, ctx.idx + idx)
            progress = len(value)
            ctx.add_token(YamlTokenMakers.new_comment(''.join(value), ''.join(ctx.obuf), self.pos()))
            self.progress_column(ctx, progress)
            self.progress_line(ctx)
            ctx.clear()
            return True

        # document ends with comment.
        value = ''.join(ctx.src[ctx.idx:])
        ctx.add_token(YamlTokenMakers.new_comment(value, ''.join(ctx.obuf), self.pos()))
        progress = len(value)
        self.progress_column(ctx, progress)
        self.progress_line(ctx)
        ctx.clear()
        return True

    def scan_multi_line(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        state = check.not_none(ctx.get_multi_line_state())
        ctx.add_origin_buf(c)

        # normalize CR and CRLF to LF
        if c == '\r':
            if ctx.next_char() == '\n':
                ctx.add_origin_buf('\n')
                self.progress(ctx, 1)
                self.offset += 1

            c = '\n'

        if ctx.is_eos():
            if self.is_first_char_at_line and c == ' ':
                state.add_indent(ctx, self.column)
            else:
                ctx.add_buf(c)

            state.update_indent_column(self.column)
            if (err := state.validate_indent_column()) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, 1)
                return _yaml_err_invalid_token(invalid_tk)

            value = ctx.buffered_src()
            ctx.add_token(YamlTokenMakers.new_string(''.join(value), ''.join(ctx.obuf), self.pos()))
            ctx.clear()
            self.progress_column(ctx, 1)

        elif self.is_new_line_char(c):
            ctx.add_buf(c)
            state.update_space_only_indent_column(self.column - 1)
            state.update_new_line_state()
            self.progress_line(ctx)
            if ctx.next():
                if self.found_document_separator_marker(ctx.src[ctx.idx:]):
                    value = ctx.buffered_src()
                    ctx.add_token(YamlTokenMakers.new_string(''.join(value), ''.join(ctx.obuf), self.pos()))
                    ctx.clear()
                    self.break_multi_line(ctx)

        elif self.is_first_char_at_line and c == ' ':
            state.add_indent(ctx, self.column)
            self.progress_column(ctx, 1)

        elif self.is_first_char_at_line and c == '\t' and state.is_indent_column(self.column):
            err = _yaml_err_invalid_token(
                YamlTokenMakers.new_invalid(
                    yaml_error('found a tab character where an indentation space is expected'),
                    ''.join(ctx.obuf),
                    self.pos(),
                ),
            )
            self.progress_column(ctx, 1)
            return err

        elif c == '\t' and not state.is_indent_column(self.column):
            ctx.add_buf_with_tab(c)
            self.progress_column(ctx, 1)

        else:
            if (err := state.validate_indent_after_space_only(self.column)) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, 1)
                return _yaml_err_invalid_token(invalid_tk)

            state.update_indent_column(self.column)
            if (err := state.validate_indent_column()) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, 1)
                return _yaml_err_invalid_token(invalid_tk)

            if (col := state.last_delim_column()) > 0:
                self.last_delim_column = col

            state.update_new_line_in_folded(ctx, self.column)
            ctx.add_buf_with_tab(c)
            self.progress_column(ctx, 1)

        return None

    def scan_new_line(self, ctx: YamlScanningContext, c: str) -> None:
        if len(ctx.buf) > 0 and self.saved_pos is None:
            buf_len = len(ctx.buffered_src())
            self.saved_pos = self.pos()
            self.saved_pos.column -= buf_len
            self.saved_pos.offset -= buf_len

        # if the following case, origin buffer has unnecessary two spaces.
        # So, `removeRightSpaceFromOriginBuf` remove them, also fix column number too.
        # ---
        # a:[space][space]
        #   b: c
        ctx.remove_right_space_from_buf()

        # There is no problem that we ignore CR which followed by LF and normalize it to LF, because of following
        # YAML1.2 spec.
        # > Line breaks inside scalar content must be normalized by the YAML processor. Each such line break must be
        #   parsed into a single line feed character.
        # > Outside scalar content, YAML allows any line break to be used to terminate lines.
        # > -- https://yaml.org/spec/1.2/spec.html
        if c == '\r' and ctx.next_char() == '\n':
            ctx.add_origin_buf('\r')
            self.progress(ctx, 1)
            self.offset += 1
            c = '\n'

        if ctx.is_eos():
            self.add_buffered_token_if_exists(ctx)
        elif self.is_anchor or self.is_alias or self.is_directive:
            self.add_buffered_token_if_exists(ctx)

        if ctx.exists_buffer() and self.is_first_char_at_line:
            if ctx.buf[-1] == ' ':
                ctx.buf[-1] = '\n'
            else:
                ctx.buf += '\n'
        else:
            ctx.add_buf(' ')

        ctx.add_origin_buf(c)
        self.progress_line(ctx)

    def is_flow_mode(self) -> bool:
        if self.started_flow_sequence_num > 0:
            return True

        if self.started_flow_map_num > 0:
            return True

        return False

    def scan_flow_map_start(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and not self.is_flow_mode():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('{')
        ctx.add_token(YamlTokenMakers.new_mapping_start(''.join(ctx.obuf), self.pos()))
        self.started_flow_map_num += 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_map_end(self, ctx: YamlScanningContext) -> bool:
        if self.started_flow_map_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('}')
        ctx.add_token(YamlTokenMakers.new_mapping_end(''.join(ctx.obuf), self.pos()))
        self.started_flow_map_num -= 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_array_start(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and not self.is_flow_mode():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('[')
        ctx.add_token(YamlTokenMakers.new_sequence_start(''.join(ctx.obuf), self.pos()))
        self.started_flow_sequence_num += 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_array_end(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and self.started_flow_sequence_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf(']')
        ctx.add_token(YamlTokenMakers.new_sequence_end(''.join(ctx.obuf), self.pos()))
        self.started_flow_sequence_num -= 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_entry(self, ctx: YamlScanningContext, c: str) -> bool:
        if self.started_flow_sequence_num <= 0 and self.started_flow_map_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf(c)
        ctx.add_token(YamlTokenMakers.new_collect_entry(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_map_delim(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        nc = ctx.next_char()
        if self.is_directive or self.is_anchor or self.is_alias:
            return False

        if (
                self.started_flow_map_num <= 0 and
                nc != ' ' and
                nc != '\t' and
                not self.is_new_line_char(nc) and
                not ctx.is_next_eos()
        ):
            return False

        if self.started_flow_map_num > 0 and nc == '/':
            # like http://
            return False

        if self.started_flow_map_num > 0:
            tk = ctx.last_token()
            if tk is not None and tk.type == YamlTokenType.MAPPING_VALUE:
                return False

        if ''.join(ctx.obuf).lstrip(' ').startswith('\t') and not ''.join(ctx.buf).startswith('\t'):
            invalid_tk = YamlTokenMakers.new_invalid(
                yaml_error('tab character cannot use as a map key directly'),
                ''.join(ctx.obuf),
                self.pos(),
            )
            self.progress_column(ctx, 1)
            return _yaml_err_invalid_token(invalid_tk)

        # mapping value
        tk = self.buffered_token(ctx)
        if tk is not None:
            self.last_delim_column = tk.position.column
            ctx.add_token(tk)

        elif (tk := ctx.last_token()) is not None:
            # If the map key is quote, the buffer does not exist because it has already been cut into tokens.
            # Therefore, we need to check the last token.
            if tk.indicator == YamlIndicator.QUOTED_SCALAR:
                self.last_delim_column = tk.position.column

        ctx.add_token(YamlTokenMakers.new_mapping_value(self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_document_start(self, ctx: YamlScanningContext) -> bool:
        if self.indent_num != 0:
            return False

        if self.column != 1:
            return False

        if ctx.repeat_num('-') != 3:
            return False

        if ctx.size > ctx.idx + 3:
            c = ctx.src[ctx.idx + 3]
            if c != ' ' and c != '\t' and c != '\n' and c != '\r':
                return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_token(YamlTokenMakers.new_document_header(''.join(ctx.obuf) + '---', self.pos()))
        self.progress_column(ctx, 3)
        ctx.clear()
        self.clear_state()
        return True

    def scan_document_end(self, ctx: YamlScanningContext) -> bool:
        if self.indent_num != 0:
            return False

        if self.column != 1:
            return False

        if ctx.repeat_num('.') != 3:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_token(YamlTokenMakers.new_document_end(''.join(ctx.obuf) + '...', self.pos()))
        self.progress_column(ctx, 3)
        ctx.clear()
        return True

    def scan_merge_key(self, ctx: YamlScanningContext) -> bool:
        if not self.is_merge_key(ctx):
            return False

        self.last_delim_column = self.column
        ctx.add_token(YamlTokenMakers.new_merge_key(''.join(ctx.obuf) + '<<', self.pos()))
        self.progress_column(ctx, 2)
        ctx.clear()
        return True

    def scan_raw_folded_char(self, ctx: YamlScanningContext) -> bool:
        if not ctx.exists_buffer():
            return False

        if not self.is_changed_to_indent_state_up():
            return False

        ctx.set_raw_folded(self.column)
        ctx.add_buf('-')
        ctx.add_origin_buf('-')
        self.progress_column(ctx, 1)
        return True

    def scan_sequence(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        nc = ctx.next_char()
        if nc != 0 and nc != ' ' and nc != '\t' and not self.is_new_line_char(nc):
            return False

        if ''.join(ctx.obuf).lstrip(' ').startswith('\t'):
            invalid_tk = YamlTokenMakers.new_invalid(
                yaml_error('tab character cannot use as a sequence delimiter'),
                ''.join(ctx.obuf),
                self.pos(),
            )
            self.progress_column(ctx, 1)
            return _yaml_err_invalid_token(invalid_tk)

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('-')
        tk = YamlTokenMakers.new_sequence_entry(''.join(ctx.obuf), self.pos())
        self.last_delim_column = tk.position.column
        ctx.add_token(tk)
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_multi_line_header(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        if (err := self.scan_multi_line_header_option(ctx)) is not None:
            return err

        self.progress_line(ctx)
        return True

    def validate_multi_line_header_option(self, opt: str) -> ta.Optional[YamlError]:
        if len(opt) == 0:
            return None

        org_opt = opt
        opt = opt.lstrip('-')
        opt = opt.lstrip('+')
        opt = opt.rstrip('-')
        opt = opt.rstrip('+')
        if len(opt) == 0:
            return None

        if opt == '0':
            return yaml_error(f'invalid header option: {org_opt!r}')

        try:
            i = int(opt, 10)
        except ValueError:
            return yaml_error(f'invalid header option: {org_opt!r}')

        if i > 9:
            return yaml_error(f'invalid header option: {org_opt!r}')

        return None

    def scan_multi_line_header_option(self, ctx: YamlScanningContext) -> ta.Optional[YamlError]:
        header = ctx.current_char()
        ctx.add_origin_buf(header)
        self.progress(ctx, 1)  # skip '|' or '>' character

        progress = 0
        crlf = False
        for idx, c in enumerate(ctx.src[ctx.idx:]):
            progress = idx
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                next_idx = ctx.idx + idx + 1
                if c == '\r' and next_idx < len(ctx.src) and ctx.src[next_idx] == '\n':
                    crlf = True
                    continue  # process \n in the next iteration

                break

        end_pos = ctx.idx + progress
        if crlf:
            # Exclude \r
            end_pos = end_pos - 1

        value = ctx.source(ctx.idx, end_pos).rstrip(' ')
        comment_value_index = value.find('#')
        opt = value
        if comment_value_index > 0:
            opt = value[:comment_value_index]

        opt = _yaml_trim_right_func(opt, lambda r: r == ' ' or r == '\t')

        if len(opt) != 0:
            if (err := self.validate_multi_line_header_option(opt)) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, progress)
                return _yaml_err_invalid_token(invalid_tk)

        if self.column == 1:
            self.last_delim_column = 1

        try:
            comment_index = ctx.obuf.index('#')
        except ValueError:
            comment_index = -1
        header_buf = ''.join(ctx.obuf)
        if comment_index > 0:
            header_buf = header_buf[:comment_index]

        if header == '|':
            ctx.add_token(YamlTokenMakers.new_literal('|' + opt, header_buf, self.pos()))
            ctx.set_literal(self.last_delim_column, opt)
        elif header == '>':
            ctx.add_token(YamlTokenMakers.new_folded('>' + opt, header_buf, self.pos()))
            ctx.set_folded(self.last_delim_column, opt)

        if comment_index > 0:
            comment = value[comment_value_index + 1:]
            self.offset += len(header_buf)
            self.column += len(header_buf)
            ctx.add_token(YamlTokenMakers.new_comment(comment, ''.join(ctx.obuf[len(header_buf):]), self.pos()))

        self.indent_state = YamlIndentState.KEEP
        ctx.reset_buffer()
        self.progress_column(ctx, progress)
        return None

    def scan_map_key(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        nc = ctx.next_char()
        if nc != ' ' and nc != '\t':
            return False

        tk = YamlTokenMakers.new_mapping_key(self.pos())
        self.last_delim_column = tk.position.column
        ctx.add_token(tk)
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_directive(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False
        if self.indent_num != 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('%')
        ctx.add_token(YamlTokenMakers.new_directive(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        self.is_directive = True
        return True

    def scan_anchor(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('&')
        ctx.add_token(YamlTokenMakers.new_anchor(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        self.is_anchor = True
        ctx.clear()
        return True

    def scan_alias(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('*')
        ctx.add_token(YamlTokenMakers.new_alias(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        self.is_alias = True
        ctx.clear()
        return True

    def scan_reserved_char(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        if ctx.exists_buffer():
            return None

        ctx.add_buf(c)
        ctx.add_origin_buf(c)
        err = _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error(f'{c!r} is a reserved character'),
                ''.join(ctx.obuf),
                self.pos(),
            ),
        )
        self.progress_column(ctx, 1)
        ctx.clear()
        return err

    def scan_tab(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        if self.started_flow_sequence_num > 0 or self.started_flow_map_num > 0:
            # tabs character is allowed in flow mode.
            return None

        if not self.is_first_char_at_line:
            return None

        ctx.add_buf(c)
        ctx.add_origin_buf(c)
        err = _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error("found character '\t' that cannot start any token"),
                ''.join(ctx.obuf),
                self.pos(),
            ),
        )
        self.progress_column(ctx, 1)
        ctx.clear()
        return err

    def _scan(self, ctx: YamlScanningContext) -> ta.Optional[YamlError]:
        while ctx.next():
            c = ctx.current_char()
            # First, change the IndentState.
            # If the target character is the first character in a line, IndentState is Up/Down/Equal state.
            # The second and subsequent letters are Keep.
            self.update_indent(ctx, c)

            # If IndentState is down, tokens are split, so the buffer accumulated until that point needs to be cutted as
            # a token.
            if self.is_changed_to_indent_state_down():
                self.add_buffered_token_if_exists(ctx)

            if ctx.is_multi_line():
                if self.is_changed_to_indent_state_down():
                    if (tk := ctx.last_token()) is not None:
                        # If literal/folded content is empty, no string token is added.
                        # Therefore, add an empty string token.
                        # But if literal/folded token column is 1, it is invalid at down state.
                        if tk.position.column == 1:
                            return yaml_error(_yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('could not find multi-line content'),
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            ))

                        if tk.type != YamlTokenType.STRING:
                            ctx.add_token(YamlTokenMakers.new_string('', '', self.pos()))

                    self.break_multi_line(ctx)

                else:
                    if (err := self.scan_multi_line(ctx, c)) is not None:
                        return err

                    continue

            if c == '{':
                if self.scan_flow_map_start(ctx):
                    continue

            elif c == '}':
                if self.scan_flow_map_end(ctx):
                    continue

            elif c == '.':
                if self.scan_document_end(ctx):
                    continue

            elif c == '<':
                if self.scan_merge_key(ctx):
                    continue

            elif c == '-':
                if self.scan_document_start(ctx):
                    continue

                if self.scan_raw_folded_char(ctx):
                    continue

                scanned = self.scan_sequence(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '[':
                if self.scan_flow_array_start(ctx):
                    continue

            elif c == ']':
                if self.scan_flow_array_end(ctx):
                    continue

            elif c == ',':
                if self.scan_flow_entry(ctx, c):
                    continue

            elif c == ':':
                scanned = self.scan_map_delim(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c in ('|', '>'):
                scanned = self.scan_multi_line_header(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '!':
                scanned = self.scan_tag(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '%':
                if self.scan_directive(ctx):
                    continue

            elif c == '?':
                if self.scan_map_key(ctx):
                    continue

            elif c == '&':
                if self.scan_anchor(ctx):
                    continue

            elif c == '*':
                if self.scan_alias(ctx):
                    continue

            elif c == '#':
                if self.scan_comment(ctx):
                    continue

            elif c in ("'", '"'):
                scanned = self.scan_quote(ctx, c)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c in ('\r', '\n'):
                self.scan_new_line(ctx, c)
                continue

            elif c == ' ':
                if self.scan_white_space(ctx):
                    continue

            elif c in ('@', '`'):
                if (err := self.scan_reserved_char(ctx, c)) is not None:
                    return err

            elif c == '\t':
                if ctx.exists_buffer() and self.last_delim_column == 0:
                    # tab indent for plain text (yaml-test-suite's spec-example-7-12-plain-lines).
                    self.indent_num += 1
                    ctx.add_origin_buf(c)
                    self.progress_only(ctx, 1)
                    continue

                if self.last_delim_column < self.column:
                    self.indent_num += 1
                    ctx.add_origin_buf(c)
                    self.progress_only(ctx, 1)
                    continue

                if (err := self.scan_tab(ctx, c)) is not None:
                    return err

            ctx.add_buf(c)
            ctx.add_origin_buf(c)
            self.progress_column(ctx, 1)

        self.add_buffered_token_if_exists(ctx)
        return None

    # init prepares the scanner s to tokenize the text src by setting the scanner at the beginning of src.
    def init(self, text: str) -> None:
        src = text
        self.source = list(src)
        self.source_pos = 0
        self.source_size = len(src)
        self.line = 1
        self.column = 1
        self.offset = 1
        self.is_first_char_at_line = True
        self.clear_state()

    def clear_state(self) -> None:
        self.prev_line_indent_num = 0
        self.last_delim_column = 0
        self.indent_level = 0
        self.indent_num = 0

    # scan scans the next token and returns the token collection. The source end is indicated by io.EOF.
    def scan(self) -> ta.Tuple[ta.Optional[YamlTokens], ta.Optional[YamlError]]:
        if self.source_pos >= self.source_size:
            return None, EofYamlError()

        ctx = YamlScanningContext.new(self.source[self.source_pos:])

        lst = YamlTokens()
        err = self._scan(ctx)
        lst.extend(ctx.tokens)

        if err is not None:
            # var invalidTokenErr *InvalidTokenError
            # if errors.As(err, &invalidTokenErr):
            #     lst = append(lst, invalidTokenErr.Token)
            return lst, err

        return lst, None


# Tokenize split to token instances from string
def yaml_tokenize(src: str) -> YamlTokens:
    s = YamlScanner()
    s.init(src)

    tks = YamlTokens()
    while True:
        sub_tokens, err = s.scan()
        if isinstance(err, EofYamlError):
            break

        tks.add(*check.not_none(sub_tokens))

    return tks


##


def _yaml_hex_to_int(s: str) -> int:
    if len(s) != 1:
        raise ValueError(s)
    b = s[0]
    if 'A' <= b <= 'F':
        return ord(b) - ord('A') + 10
    if 'a' <= b <= 'f':
        return ord(b) - ord('a') + 10
    return ord(b) - ord('0')


def _yaml_hex_runes_to_int(b: ta.List[str]) -> int:
    n = 0
    for i in range(len(b)):
        n += _yaml_hex_to_int(b[i]) << ((len(b) - i - 1) * 4)
    return n


def _yaml_trim_right_func(s: str, predicate: ta.Callable[[str], bool]) -> str:
    if not s:
        return s

    i = len(s) - 1
    while i >= 0 and predicate(s[i]):
        i -= 1

    return s[:i + 1]


########################################
# ../parsing.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


# context context at parsing
@dc.dataclass()
class YamlParsingContext:
    token_ref: ta.Optional['YamlParseTokenRef'] = None
    path: str = dc.field(default_factory=dataclass_field_required('path'))
    is_flow: bool = False

    def current_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        if ref.idx >= ref.size:
            return None

        return ref.tokens[ref.idx]

    def is_comment(self) -> bool:
        return YamlParseToken.type(self.current_token()) == YamlTokenType.COMMENT

    def next_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        if ref.idx + 1 >= ref.size:
            return None

        return ref.tokens[ref.idx + 1]

    def next_not_comment_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        for i in range(ref.idx + 1, ref.size):
            tk = ref.tokens[i]
            if tk.type() == YamlTokenType.COMMENT:
                continue
            return tk

        return None

    def is_token_not_found(self) -> bool:
        return self.current_token() is None

    def with_group(self, g: 'YamlParseTokenGroup') -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.token_ref = YamlParseTokenRef(
            tokens=g.tokens,
            size=len(g.tokens),
        )
        return ctx

    def with_child(self, path: str) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.path = self.path + '.' + yaml_normalize_path(path)
        return ctx

    def with_index(self, idx: int) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.path = self.path + '[' + str(idx) + ']'
        return ctx

    def with_flow(self, is_flow: bool) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.is_flow = is_flow
        return ctx

    @staticmethod
    def new() -> 'YamlParsingContext':
        return YamlParsingContext(
            path='$',
        )

    def go_next(self) -> None:
        ref = check.not_none(self.token_ref)
        if ref.size <= ref.idx + 1:
            ref.idx = ref.size
        else:
            ref.idx += 1

    def next(self) -> bool:
        return check.not_none(self.token_ref).idx < check.not_none(self.token_ref).size

    def insert_null_token(self, tk: 'YamlParseToken') -> 'YamlParseToken':
        null_token = self.create_implicit_null_token(tk)
        self.insert_token(null_token)
        self.go_next()

        return null_token

    def add_null_value_token(self, tk: 'YamlParseToken') -> 'YamlParseToken':
        null_token = self.create_implicit_null_token(tk)
        raw_tk = null_token.raw_token()

        # add space for map or sequence value.
        check.not_none(raw_tk).position.column += 1

        self.add_token(null_token)
        self.go_next()

        return null_token

    def create_implicit_null_token(self, base: 'YamlParseToken') -> 'YamlParseToken':
        pos = copy.copy(check.not_none(base.raw_token()).position)
        pos.column += 1
        tk = yaml_new_token('null', ' null', pos)
        tk.type = YamlTokenType.IMPLICIT_NULL
        return YamlParseToken(token=tk)

    def insert_token(self, tk: 'YamlParseToken') -> None:
        ref = check.not_none(self.token_ref)
        idx = ref.idx
        if ref.size < idx:
            return

        if ref.size == idx:
            cur_token = ref.tokens[ref.size - 1]
            check.not_none(tk.raw_token()).next = cur_token.raw_token()
            check.not_none(cur_token.raw_token()).prev = tk.raw_token()

            ref.tokens.append(tk)
            ref.size = len(ref.tokens)
            return

        cur_token = ref.tokens[idx]
        check.not_none(tk.raw_token()).next = cur_token.raw_token()
        check.not_none(cur_token.raw_token()).prev = tk.raw_token()

        ref.tokens = [*ref.tokens[:idx + 1], *ref.tokens[idx:]]
        ref.tokens[idx] = tk
        ref.size = len(ref.tokens)

    def add_token(self, tk: 'YamlParseToken') -> None:
        ref = check.not_none(self.token_ref)
        last_tk = check.not_none(ref.tokens[ref.size - 1])
        if last_tk.group is not None:
            last_tk = check.not_none(last_tk.group.last())

        check.not_none(last_tk.raw_token()).next = tk.raw_token()
        check.not_none(tk.raw_token()).prev = last_tk.raw_token()

        ref.tokens.append(tk)
        ref.size = len(ref.tokens)


@dc.dataclass()
class YamlParseTokenRef:
    tokens: ta.List['YamlParseToken']
    size: int
    idx: int = 0


##


YAML_PATH_SPECIAL_CHARS = (
    '$',
    '*',
    '.',
    '[',
    ']',
)


def yaml_contains_path_special_char(path: str) -> bool:
    return any(char in path for char in YAML_PATH_SPECIAL_CHARS)


def yaml_normalize_path(path: str) -> str:
    if yaml_contains_path_special_char(path):
        return f"'{path}'"

    return path


##


# Option represents parser's option.
YamlOption = ta.Callable[['YamlParser'], None]  # ta.TypeAlias  # omlish-amalg-typing-no-move


# AllowDuplicateMapKey allow the use of keys with the same name in the same map, but by default, this is not permitted.
def yaml_allow_duplicate_map_key() -> YamlOption:
    def fn(p: 'YamlParser') -> None:
        p.allow_duplicate_map_key = True

    return fn


##


class YamlParseTokenGroupType(enum.Enum):
    NONE = enum.auto()
    DIRECTIVE = enum.auto()
    DIRECTIVE_NAME = enum.auto()
    DOCUMENT = enum.auto()
    DOCUMENT_BODY = enum.auto()
    ANCHOR = enum.auto()
    ANCHOR_NAME = enum.auto()
    ALIAS = enum.auto()
    LITERAL = enum.auto()
    FOLDED = enum.auto()
    SCALAR_TAG = enum.auto()
    MAP_KEY = enum.auto()
    MAP_KEY_VALUE = enum.auto()


@dc.dataclass()
class YamlParseToken:
    token: ta.Optional[YamlToken] = None
    group: ta.Optional['YamlParseTokenGroup'] = None
    line_comment: ta.Optional[YamlToken] = None

    def raw_token(self: ta.Optional['YamlParseToken']) -> ta.Optional[YamlToken]:
        if self is None:
            return None
        if self.token is not None:
            return self.token
        return check.not_none(self.group).raw_token()

    def type(self: ta.Optional['YamlParseToken']) -> YamlTokenType:
        if self is None:
            return YamlTokenType.UNKNOWN
        if self.token is not None:
            return self.token.type
        return check.not_none(self.group).token_type()

    def group_type(self: ta.Optional['YamlParseToken']) -> YamlParseTokenGroupType:
        if self is None:
            return YamlParseTokenGroupType.NONE
        if self.token is not None:
            return YamlParseTokenGroupType.NONE
        return check.not_none(self.group).type

    def line(self: ta.Optional['YamlParseToken']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.line
        return check.not_none(self.group).line()

    def column(self: ta.Optional['YamlParseToken']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.column
        return check.not_none(self.group).column()

    def set_group_type(self, typ: YamlParseTokenGroupType) -> None:
        if self.group is None:
            return
        self.group.type = typ


##


@dc.dataclass()
class YamlParseTokenGroup:
    type: YamlParseTokenGroupType = YamlParseTokenGroupType.NONE
    tokens: ta.List[YamlParseToken] = dc.field(default_factory=dataclass_field_required('tokens'))

    def first(self) -> ta.Optional[YamlParseToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def last(self) -> ta.Optional[YamlParseToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[len(self.tokens) - 1]

    def raw_token(self) -> ta.Optional[YamlToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0].raw_token()

    def line(self) -> int:
        if len(self.tokens) == 0:
            return 0
        return self.tokens[0].line()

    def column(self) -> int:
        if len(self.tokens) == 0:
            return 0
        return self.tokens[0].column()

    def token_type(self) -> YamlTokenType:
        if len(self.tokens) == 0:
            return YamlTokenType.UNKNOWN
        return self.tokens[0].type()


def yaml_create_grouped_tokens(tokens: YamlTokens) -> YamlErrorOr[ta.List[YamlParseToken]]:
    tks = yaml_new_tokens(tokens)

    tks = yaml_create_line_comment_token_groups(tks)

    tks_ = yaml_create_literal_and_folded_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_anchor_and_alias_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_scalar_tag_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_anchor_with_scalar_tag_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_map_key_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks = yaml_create_map_key_value_token_groups(tks)

    tks_ = yaml_create_directive_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_document_tokens(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    return tks


def yaml_new_tokens(tks: YamlTokens) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    for tk in tks:
        ret.append(YamlParseToken(token=tk))
    return ret


def yaml_create_line_comment_token_groups(tokens: ta.List[YamlParseToken]) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    for i in range(len(tokens)):
        tk = tokens[i]
        if tk.type() == YamlTokenType.COMMENT:
            if i > 0 and tokens[i - 1].line() == tk.line():
                tokens[i - 1].line_comment = tk.raw_token()
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def yaml_create_literal_and_folded_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:  # noqa
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.LITERAL:
            tks: ta.List[YamlParseToken] = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.LITERAL,
                    tokens=tks,
                ),
            ))
            i += 1
        elif tk.type() == YamlTokenType.FOLDED:
            tks = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.FOLDED,
                    tokens=tks,
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def yaml_create_anchor_and_alias_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.ANCHOR:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined anchor name', tk.raw_token())
            if i + 2 >= len(tokens):
                return YamlSyntaxError('undefined anchor value', tk.raw_token())
            anchor_name = YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.ANCHOR_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            value_tk = tokens[i + 2]
            if tk.line() == value_tk.line() and value_tk.type() == YamlTokenType.SEQUENCE_ENTRY:
                return YamlSyntaxError(
                    'sequence entries are not allowed after anchor on the same line',
                    value_tk.raw_token(),
                )
            if tk.line() == value_tk.line() and yaml_is_scalar_type(value_tk):
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.ANCHOR,
                        tokens=[anchor_name, value_tk],
                    ),
                ))
                i += 1
            else:
                ret.append(anchor_name)
            i += 1
        elif tk.type() == YamlTokenType.ALIAS:
            if i + 1 == len(tokens):
                return YamlSyntaxError('undefined alias name', tk.raw_token())
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.ALIAS,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def yaml_create_scalar_tag_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() != YamlTokenType.TAG:
            ret.append(tk)
            continue
        tag = check.not_none(tk.raw_token())
        if tag.value.startswith('!!'):
            # secondary tag.
            if tag.value in (
                    YamlReservedTagKeywords.INTEGER,
                    YamlReservedTagKeywords.FLOAT,
                    YamlReservedTagKeywords.STRING,
                    YamlReservedTagKeywords.BINARY,
                    YamlReservedTagKeywords.TIMESTAMP,
                    YamlReservedTagKeywords.BOOLEAN,
                    YamlReservedTagKeywords.NULL,
            ):
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if yaml_is_scalar_type(tokens[i + 1]):
                    ret.append(YamlParseToken(
                        group=YamlParseTokenGroup(
                            type=YamlParseTokenGroupType.SCALAR_TAG,
                            tokens=[tk, tokens[i + 1]],
                        ),
                    ))
                    i += 1
                else:
                    ret.append(tk)
            elif tag.value == YamlReservedTagKeywords.MERGE:
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if tokens[i + 1].type() != YamlTokenType.MERGE_KEY:
                    return YamlSyntaxError('could not find merge key', tokens[i + 1].raw_token())
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.SCALAR_TAG,
                        tokens=[tk, tokens[i + 1]],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
        else:
            if len(tokens) <= i + 1:
                ret.append(tk)
                continue
            if tk.line() != tokens[i + 1].line():
                ret.append(tk)
                continue
            if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if yaml_is_flow_type(tokens[i + 1]):
                ret.append(tk)
                continue
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.SCALAR_TAG,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
    return ret


def yaml_create_anchor_with_scalar_tag_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:  # noqa
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined anchor value', tk.raw_token())
            value_tk = tokens[i + 1]
            if tk.line() == value_tk.line() and value_tk.group_type() == YamlParseTokenGroupType.SCALAR_TAG:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.ANCHOR,
                        tokens=[tk, tokens[i + 1]],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def yaml_create_map_key_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    tks = yaml_create_map_key_by_mapping_key(tokens)
    if isinstance(tks, YamlError):
        return tks
    return yaml_create_map_key_by_mapping_value(tks)


def yaml_create_map_key_by_mapping_key(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.MAPPING_KEY:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined map key', tk.raw_token())
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.MAP_KEY,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def yaml_create_map_key_by_mapping_value(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.MAPPING_VALUE:
            if i == 0:
                return YamlSyntaxError('unexpected key name', tk.raw_token())
            map_key_tk = tokens[i - 1]
            if yaml_is_not_map_key_type(map_key_tk):
                return YamlSyntaxError('found an invalid key for this map', tokens[i].raw_token())
            new_tk = YamlParseToken(
                token=map_key_tk.token,
                group=map_key_tk.group,
            )
            map_key_tk.token = None
            map_key_tk.group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.MAP_KEY,
                tokens=[new_tk, tk],
            )
        else:
            ret.append(tk)
    return ret


def yaml_create_map_key_value_token_groups(tokens: ta.List[YamlParseToken]) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == YamlParseTokenGroupType.MAP_KEY:
            if len(tokens) <= i + 1:
                ret.append(tk)
                continue
            value_tk = tokens[i + 1]
            if tk.line() != value_tk.line():
                ret.append(tk)
                continue
            if value_tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if (
                    value_tk.type() == YamlTokenType.TAG and
                    value_tk.group_type() != YamlParseTokenGroupType.SCALAR_TAG
            ):
                ret.append(tk)
                continue

            if yaml_is_scalar_type(value_tk) or value_tk.type() == YamlTokenType.TAG:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.MAP_KEY_VALUE,
                        tokens=[tk, value_tk],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
                continue
        else:
            ret.append(tk)
    return ret


def yaml_create_directive_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.DIRECTIVE:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined directive value', tk.raw_token())
            directive_name = YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.DIRECTIVE_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            i += 1
            value_tks: ta.List[YamlParseToken] = []
            for j in range(i + 1, len(tokens)):
                if tokens[j].line() != tk.line():
                    break
                value_tks.append(tokens[j])
                i += 1
            if i + 1 >= len(tokens) or tokens[i + 1].type() != YamlTokenType.DOCUMENT_HEADER:
                return YamlSyntaxError('unexpected directive value. document not started', tk.raw_token())
            if len(value_tks) != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DIRECTIVE,
                        tokens=[directive_name, *value_tks],
                    ),
                ))
            else:
                ret.append(directive_name)
        else:
            ret.append(tk)
    return ret


def yaml_create_document_tokens(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.DOCUMENT_HEADER:
            if i != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(tokens=tokens[:i]),
                ))
            if i + 1 == len(tokens):
                # if current token is last token, add DocumentHeader only tokens to ret.
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i + 1].type() == YamlTokenType.DOCUMENT_HEADER:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i].line() == tokens[i + 1].line():
                if tokens[i + 1].group_type() in (
                        YamlParseTokenGroupType.MAP_KEY,
                        YamlParseTokenGroupType.MAP_KEY_VALUE,
                ):
                    return YamlSyntaxError(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
                if tokens[i + 1].type() == YamlTokenType.SEQUENCE_ENTRY:
                    return YamlSyntaxError(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
            tks = yaml_create_document_tokens(tokens[i + 1:])
            if isinstance(tks, YamlError):
                return tks
            if len(tks) != 0:
                tks[0].set_group_type(YamlParseTokenGroupType.DOCUMENT)
                check.not_none(tks[0].group).tokens = list(check.not_none(tks[0].group).tokens)
                ret.extend(tks)
                return ret
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.DOCUMENT,
                    tokens=[tk],
                ),
            ))
            return ret
        elif tk.type() == YamlTokenType.DOCUMENT_END:
            if i != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=tokens[0: i + 1],
                    ),
                ))
            if i + 1 == len(tokens):
                return ret
            if yaml_is_scalar_type(tokens[i + 1]):
                return YamlSyntaxError('unexpected end content', tokens[i + 1].raw_token())

            tks = yaml_create_document_tokens(tokens[i + 1:])
            if isinstance(tks, YamlError):
                return tks
            ret.extend(tks)
            return ret
    ret.append(YamlParseToken(
        group=YamlParseTokenGroup(
            type=YamlParseTokenGroupType.DOCUMENT,
            tokens=tokens,
        ),
    ))
    return ret


def yaml_is_scalar_type(tk: YamlParseToken) -> bool:
    if tk.group_type() in (YamlParseTokenGroupType.MAP_KEY, YamlParseTokenGroupType.MAP_KEY_VALUE):
        return False
    typ = tk.type()
    return typ in (
        YamlTokenType.ANCHOR,
        YamlTokenType.ALIAS,
        YamlTokenType.LITERAL,
        YamlTokenType.FOLDED,
        YamlTokenType.NULL,
        YamlTokenType.IMPLICIT_NULL,
        YamlTokenType.BOOL,
        YamlTokenType.INTEGER,
        YamlTokenType.BINARY_INTEGER,
        YamlTokenType.OCTET_INTEGER,
        YamlTokenType.HEX_INTEGER,
        YamlTokenType.FLOAT,
        YamlTokenType.INFINITY,
        YamlTokenType.NAN,
        YamlTokenType.STRING,
        YamlTokenType.SINGLE_QUOTE,
        YamlTokenType.DOUBLE_QUOTE,
    )


def yaml_is_not_map_key_type(tk: YamlParseToken) -> bool:
    typ = tk.type()
    return typ in (
        YamlTokenType.DIRECTIVE,
        YamlTokenType.DOCUMENT_HEADER,
        YamlTokenType.DOCUMENT_END,
        YamlTokenType.COLLECT_ENTRY,
        YamlTokenType.MAPPING_START,
        YamlTokenType.MAPPING_VALUE,
        YamlTokenType.MAPPING_END,
        YamlTokenType.SEQUENCE_START,
        YamlTokenType.SEQUENCE_ENTRY,
        YamlTokenType.SEQUENCE_END,
    )


def yaml_is_flow_type(tk: YamlParseToken) -> bool:
    typ = tk.type()
    return typ in (
        YamlTokenType.MAPPING_START,
        YamlTokenType.MAPPING_END,
        YamlTokenType.SEQUENCE_START,
        YamlTokenType.SEQUENCE_ENTRY,
    )


##


class YamlNodeMakers:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @staticmethod
    def new_mapping_node(
            ctx: YamlParsingContext,
            tk: YamlParseToken,
            is_flow: bool,
            *values: MappingValueYamlNode,
    ) -> YamlErrorOr[MappingYamlNode]:
        node = YamlAsts.mapping(check.not_none(tk.raw_token()), is_flow, *values)
        node.set_path(ctx.path)
        return node

    @staticmethod
    def new_mapping_value_node(
            ctx: YamlParsingContext,
            colon_tk: YamlParseToken,
            entry_tk: ta.Optional[YamlParseToken],
            key: MapKeyYamlNode,
            value: YamlNode,
    ) -> YamlErrorOr[MappingValueYamlNode]:
        node = YamlAsts.mapping_value(check.not_none(colon_tk.raw_token()), key, value)
        node.set_path(ctx.path)
        node.collect_entry = YamlParseToken.raw_token(entry_tk)
        if check.not_none(key.get_token()).position.line == check.not_none(value.get_token()).position.line:
            # originally key was commented, but now that null value has been added, value must be commented.
            if (err := yaml_set_line_comment(ctx, value, colon_tk)) is not None:
                return err
            # set line comment by colon_tk or entry_tk.
            if (err := yaml_set_line_comment(ctx, value, entry_tk)) is not None:
                return err
        else:
            if (err := yaml_set_line_comment(ctx, key, colon_tk)) is not None:
                return err
            # set line comment by colon_tk or entry_tk.
            if (err := yaml_set_line_comment(ctx, key, entry_tk)) is not None:
                return err
        return node

    @staticmethod
    def new_mapping_key_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[MappingKeyYamlNode]:  # noqa
        node = YamlAsts.mapping_key(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_anchor_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[AnchorYamlNode]:
        node = YamlAsts.anchor(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_alias_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[AliasYamlNode]:
        node = YamlAsts.alias(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_directive_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[DirectiveYamlNode]:  # noqa
        node = YamlAsts.directive(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_merge_key_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[MergeKeyYamlNode]:  # noqa
        node = YamlAsts.merge_key(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_null_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[NullYamlNode]:
        node = YamlAsts.null(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_bool_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[BoolYamlNode]:
        node = YamlAsts.bool_(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_integer_node(ctx: YamlParsingContext, tk: YamlParseToken) -> YamlErrorOr[IntegerYamlNode]:
        node = YamlAsts.integer(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_float_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[FloatYamlNode]:
        node = YamlAsts.float_(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_infinity_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[InfinityYamlNode]:  # noqa
        node = YamlAsts.infinity(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_nan_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[NanYamlNode]:
        node = YamlAsts.nan(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_string_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[StringYamlNode]:
        node = YamlAsts.string(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_literal_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[LiteralYamlNode]:
        node = YamlAsts.literal(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_tag_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[TagYamlNode]:
        node = YamlAsts.tag(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_sequence_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken], is_flow: bool) -> YamlErrorOr[SequenceYamlNode]:  # noqa
        node = YamlAsts.sequence(check.not_none(YamlParseToken.raw_token(tk)), is_flow)
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_tag_default_scalar_value_node(ctx: YamlParsingContext, tag: YamlToken) -> YamlErrorOr[ScalarYamlNode]:
        pos = copy.copy(tag.position)
        pos.column += 1

        tk: YamlErrorOr[YamlParseToken]
        node: YamlErrorOr[ScalarYamlNode]

        if tag.value == YamlReservedTagKeywords.INTEGER:
            tk = YamlParseToken(token=yaml_new_token('0', '0', pos))
            n0 = YamlNodeMakers.new_integer_node(ctx, tk)
            if isinstance(n0, YamlError):
                return n0
            node = n0
        elif tag.value == YamlReservedTagKeywords.FLOAT:
            tk = YamlParseToken(token=yaml_new_token('0', '0', pos))
            n1 = YamlNodeMakers.new_float_node(ctx, tk)
            if isinstance(n1, YamlError):
                return n1
            node = n1
        elif tag.value in (
                YamlReservedTagKeywords.STRING,
                YamlReservedTagKeywords.BINARY,
                YamlReservedTagKeywords.TIMESTAMP,
        ):
            tk = YamlParseToken(token=yaml_new_token('', '', pos))
            n2 = YamlNodeMakers.new_string_node(ctx, tk)
            if isinstance(n2, YamlError):
                return n2
            node = n2
        elif tag.value == YamlReservedTagKeywords.BOOLEAN:
            tk = YamlParseToken(token=yaml_new_token('false', 'false', pos))
            n3 = YamlNodeMakers.new_bool_node(ctx, tk)
            if isinstance(n3, YamlError):
                return n3
            node = n3
        elif tag.value == YamlReservedTagKeywords.NULL:
            tk = YamlParseToken(token=yaml_new_token('null', 'null', pos))
            n4 = YamlNodeMakers.new_null_node(ctx, tk)
            if isinstance(n4, YamlError):
                return n4
            node = n4
        else:
            return YamlSyntaxError(f'cannot assign default value for {tag.value!r} tag', tag)
        ctx.insert_token(tk)
        ctx.go_next()
        return node


def yaml_set_line_comment(ctx: YamlParsingContext, node: YamlNode, tk: ta.Optional[YamlParseToken]) -> ta.Optional[YamlError]:  # noqa
    if tk is None or tk.line_comment is None:
        return None
    comment = YamlAsts.comment_group([tk.line_comment])
    comment.set_path(ctx.path)
    if (err := node.set_comment(comment)) is not None:
        return err
    return None


def yaml_set_head_comment(cm: ta.Optional[CommentGroupYamlNode], value: YamlNode) -> ta.Optional[YamlError]:
    if cm is None:
        return None
    n = value
    if isinstance(n, MappingYamlNode):
        if len(n.values) != 0 and value.get_comment() is None:
            cm.set_path(n.values[0].get_path())
            return n.values[0].set_comment(cm)
    elif isinstance(n, MappingValueYamlNode):
        cm.set_path(n.get_path())
        return n.set_comment(cm)
    cm.set_path(value.get_path())
    return value.set_comment(cm)


##


YamlParseMode = int  # ta.TypeAlias  # omlish-amalg-typing-no-move

YAML_PARSE_COMMENTS = YamlParseMode(1)  # parse comments and add them to AST


# ParseBytes parse from byte slice, and returns YamlFile
def yaml_parse_str(
        s: str,
        mode: YamlParseMode = YamlParseMode(0),
        *opts: YamlOption,
) -> YamlErrorOr[YamlFile]:
    tokens = yaml_tokenize(s)
    f = yaml_parse(tokens, mode, *opts)
    if isinstance(f, YamlError):
        return f
    return f


# Parse parse from token instances, and returns YamlFile
def yaml_parse(
        tokens: YamlTokens,
        mode: YamlParseMode = YamlParseMode(0),
        *opts: YamlOption,
) -> YamlErrorOr[YamlFile]:
    if (tk := tokens.invalid_token()) is not None:
        return YamlSyntaxError(check.not_none(tk.error).message, tk)
    p = YamlParser.new_parser(tokens, mode, opts)
    if isinstance(p, YamlError):
        return p
    f = p.parse(YamlParsingContext.new())
    if isinstance(f, YamlError):
        return f
    return f


#


YamlVersion = str  # ta.TypeAlias  # omlish-amalg-typing-no-move

YAML10 = YamlVersion('1.0')
YAML11 = YamlVersion('1.1')
YAML12 = YamlVersion('1.2')
YAML13 = YamlVersion('1.3')

YAML_VERSION_MAP: ta.Mapping[str, YamlVersion] = {
    '1.0': YAML10,
    '1.1': YAML11,
    '1.2': YAML12,
    '1.3': YAML13,
}


#

@dc.dataclass()
class YamlParser:
    tokens: ta.List[YamlParseToken]
    path_map: ta.Dict[str, YamlNode]
    yaml_version: YamlVersion = YamlVersion('')
    allow_duplicate_map_key: bool = False
    secondary_tag_directive: ta.Optional[DirectiveYamlNode] = None

    @staticmethod
    def new_parser(
            tokens: YamlTokens,
            mode: YamlParseMode,
            opts: ta.Iterable[YamlOption],
    ) -> YamlErrorOr['YamlParser']:
        filtered_tokens: ta.List[YamlToken] = []
        if mode & YAML_PARSE_COMMENTS != 0:
            filtered_tokens = tokens
        else:
            for tk in tokens:
                if tk.type == YamlTokenType.COMMENT:
                    continue
                # keep prev/next reference between tokens containing comments
                # https://github.com/goccy/go-yaml/issues/254
                filtered_tokens.append(tk)
        tks = yaml_create_grouped_tokens(YamlTokens(filtered_tokens))
        if isinstance(tks, YamlError):
            return tks
        p = YamlParser(
            tokens=tks,
            path_map={},
        )
        for opt in opts:
            opt(p)
        return p

    def parse(self, ctx: YamlParsingContext) -> YamlErrorOr[YamlFile]:
        file = YamlFile(docs=[])
        for token in self.tokens:
            doc = self.parse_document(ctx, check.not_none(token.group))
            if isinstance(doc, YamlError):
                return doc
            file.docs.append(doc)
        return file

    def parse_document(
            self,
            ctx: YamlParsingContext,
            doc_group: YamlParseTokenGroup,
    ) -> YamlErrorOr[DocumentYamlNode]:
        if len(doc_group.tokens) == 0:
            return YamlAsts.document(doc_group.raw_token(), None)

        self.path_map: ta.Dict[str, YamlNode] = {}

        tokens = doc_group.tokens
        start: ta.Optional[YamlToken] = None
        end: ta.Optional[YamlToken] = None
        if YamlParseToken.type(doc_group.first()) == YamlTokenType.DOCUMENT_HEADER:
            start = YamlParseToken.raw_token(doc_group.first())
            tokens = tokens[1:]

        clear_yaml_version = False
        try:
            if YamlParseToken.type(doc_group.last()) == YamlTokenType.DOCUMENT_END:
                end = YamlParseToken.raw_token(doc_group.last())
                tokens = tokens[:len(tokens) - 1]
                # clear yaml version value if DocumentEnd token (...) is specified.
                clear_yaml_version = True

            if len(tokens) == 0:
                return YamlAsts.document(doc_group.raw_token(), None)

            body = self.parse_document_body(ctx.with_group(YamlParseTokenGroup(
                type=YamlParseTokenGroupType.DOCUMENT_BODY,
                tokens=tokens,
            )))
            if isinstance(body, YamlError):
                return body
            node = YamlAsts.document(start, body)
            node.end = end
            return node

        finally:
            if clear_yaml_version:
                self.yaml_version = ''

    def parse_document_body(self, ctx: YamlParsingContext) -> YamlErrorOr[YamlNode]:
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if ctx.next():
            return YamlSyntaxError('value is not allowed in this context', YamlParseToken.raw_token(ctx.current_token()))  # noqa
        return node

    def parse_token(self, ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[YamlNode]:
        if YamlParseToken.group_type(tk) in (
                YamlParseTokenGroupType.MAP_KEY,
                YamlParseTokenGroupType.MAP_KEY_VALUE,
        ):
            return self.parse_map(ctx)

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.DIRECTIVE:
            node0 = self.parse_directive(
                ctx.with_group(check.not_none(check.not_none(tk).group)),
                check.not_none(check.not_none(tk).group),
            )
            if isinstance(node0, YamlError):
                return node0
            ctx.go_next()
            return node0

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.DIRECTIVE_NAME:
            node1 = self.parse_directive_name(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node1, YamlError):
                return node1
            ctx.go_next()
            return node1

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR:
            node2 = self.parse_anchor(
                ctx.with_group(check.not_none(check.not_none(tk).group)),
                check.not_none(check.not_none(tk).group),
            )
            if isinstance(node2, YamlError):
                return node2
            ctx.go_next()
            return node2

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME:
            anchor = self.parse_anchor_name(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            if ctx.is_token_not_found():
                return YamlSyntaxError('could not find anchor value', YamlParseToken.raw_token(tk))
            value = self.parse_token(ctx, ctx.current_token())
            if isinstance(value, YamlError):
                return value
            if isinstance(value, AnchorYamlNode):
                return YamlSyntaxError('anchors cannot be used consecutively', value.get_token())
            anchor.value = value
            return anchor

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ALIAS:
            node3 = self.parse_alias(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node3, YamlError):
                return node3
            ctx.go_next()
            return node3

        elif YamlParseToken.group_type(tk) in (
                YamlParseTokenGroupType.LITERAL,
                YamlParseTokenGroupType.FOLDED,
        ):
            node4 = self.parse_literal(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node4, YamlError):
                return node4
            ctx.go_next()
            return node4

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.SCALAR_TAG:
            node5 = self.parse_tag(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node5, YamlError):
                return node5
            ctx.go_next()
            return node5

        if YamlParseToken.type(tk) == YamlTokenType.COMMENT:
            return ta.cast('YamlErrorOr[YamlNode]', check.not_none(self.parse_comment(ctx)))

        elif YamlParseToken.type(tk) == YamlTokenType.TAG:
            return self.parse_tag(ctx)

        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_START:
            return self.parse_flow_map(ctx.with_flow(True))

        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_START:
            return self.parse_flow_sequence(ctx.with_flow(True))

        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY:
            return self.parse_sequence(ctx)

        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_END:
            # SequenceEndType is always validated in parse_flow_sequence.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return YamlSyntaxError("could not find '[' character corresponding to ']'", YamlParseToken.raw_token(tk))

        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_END:
            # MappingEndType is always validated in parse_flow_map.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return YamlSyntaxError("could not find '{' character corresponding to '}'", YamlParseToken.raw_token(tk))

        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_VALUE:
            return YamlSyntaxError('found an invalid key for this map', YamlParseToken.raw_token(tk))

        node6 = self.parse_scalar_value(ctx, tk)
        if isinstance(node6, YamlError):
            return node6

        ctx.go_next()
        return check.not_none(node6)

    def parse_scalar_value(self, ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ta.Optional[ScalarYamlNode]]:  # noqa
        tk = check.not_none(tk)
        if tk.group is not None:
            if tk.group_type() == YamlParseTokenGroupType.ANCHOR:
                return self.parse_anchor(ctx.with_group(tk.group), tk.group)

            elif tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                anchor = self.parse_anchor_name(ctx.with_group(tk.group))
                if isinstance(anchor, YamlError):
                    return anchor
                ctx.go_next()
                if ctx.is_token_not_found():
                    return YamlSyntaxError('could not find anchor value', tk.raw_token())
                value = self.parse_token(ctx, ctx.current_token())
                if isinstance(value, YamlError):
                    return value
                if isinstance(value, AnchorYamlNode):
                    return YamlSyntaxError('anchors cannot be used consecutively', value.get_token())
                anchor.value = value
                return anchor

            elif tk.group_type() == YamlParseTokenGroupType.ALIAS:
                return self.parse_alias(ctx.with_group(tk.group))

            elif tk.group_type() in (
                    YamlParseTokenGroupType.LITERAL,
                    YamlParseTokenGroupType.FOLDED,
            ):
                return self.parse_literal(ctx.with_group(tk.group))

            elif tk.group_type() == YamlParseTokenGroupType.SCALAR_TAG:
                return self.parse_tag(ctx.with_group(tk.group))

            else:
                return YamlSyntaxError('unexpected scalar value', tk.raw_token())

        if tk.type() == YamlTokenType.MERGE_KEY:
            return YamlNodeMakers.new_merge_key_node(ctx, tk)

        if tk.type() in (YamlTokenType.NULL, YamlTokenType.IMPLICIT_NULL):
            return YamlNodeMakers.new_null_node(ctx, tk)

        if tk.type() == YamlTokenType.BOOL:
            return YamlNodeMakers.new_bool_node(ctx, tk)

        if tk.type() in (
                YamlTokenType.INTEGER,
                YamlTokenType.BINARY_INTEGER,
                YamlTokenType.OCTET_INTEGER,
                YamlTokenType.HEX_INTEGER,
        ):
            return YamlNodeMakers.new_integer_node(ctx, tk)

        if tk.type() == YamlTokenType.FLOAT:
            return YamlNodeMakers.new_float_node(ctx, tk)

        if tk.type() == YamlTokenType.INFINITY:
            return YamlNodeMakers.new_infinity_node(ctx, tk)

        if tk.type() == YamlTokenType.NAN:
            return YamlNodeMakers.new_nan_node(ctx, tk)

        if tk.type() in (
                YamlTokenType.STRING,
                YamlTokenType.SINGLE_QUOTE,
                YamlTokenType.DOUBLE_QUOTE,
        ):
            return YamlNodeMakers.new_string_node(ctx, tk)

        if tk.type() == YamlTokenType.TAG:
            # this case applies when it is a scalar tag and its value does not exist.
            # Examples of cases where the value does not exist include cases like `key: !!str,` or `!!str : value`.
            return self.parse_scalar_tag(ctx)

        return YamlSyntaxError('unexpected scalar value type', tk.raw_token())

    def parse_flow_map(self, ctx: YamlParsingContext) -> YamlErrorOr[MappingYamlNode]:
        node = YamlNodeMakers.new_mapping_node(ctx, check.not_none(ctx.current_token()), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip MappingStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if YamlParseToken.type(tk) == YamlTokenType.MAPPING_END:
                node.end = YamlParseToken.raw_token(tk)
                break

            entry_tk: ta.Optional[YamlParseToken] = None
            if YamlParseToken.type(tk) == YamlTokenType.COLLECT_ENTRY:
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return YamlSyntaxError("',' or '}' must be specified", YamlParseToken.raw_token(tk))

            if YamlParseToken.type(tk := ctx.current_token()) == YamlTokenType.MAPPING_END:
                # this case is here: "{ elem, }".
                # In this case, ignore the last element and break mapping parsing.
                node.end = YamlParseToken.raw_token(tk)
                break

            map_key_tk = ctx.current_token()
            if YamlParseToken.group_type(map_key_tk) == YamlParseTokenGroupType.MAP_KEY_VALUE:
                value0 = self.parse_map_key_value(
                    ctx.with_group(check.not_none(check.not_none(map_key_tk).group)),
                    check.not_none(check.not_none(map_key_tk).group),
                    entry_tk,
                )
                if isinstance(value0, YamlError):
                    return value0
                node.values.append(value0)
                ctx.go_next()

            elif YamlParseToken.group_type(map_key_tk) == YamlParseTokenGroupType.MAP_KEY:
                key0 = self.parse_map_key(
                    ctx.with_group(check.not_none(check.not_none(map_key_tk).group)),
                    check.not_none(check.not_none(map_key_tk).group),
                )
                if isinstance(key0, YamlError):
                    return key0
                ctx = ctx.with_child(self.map_key_text(key0))
                colon_tk = check.not_none(check.not_none(map_key_tk).group).last()

                if self.is_flow_map_delim(check.not_none(ctx.next_token())):
                    value1 = YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(check.not_none(colon_tk)))
                    if isinstance(value1, YamlError):
                        return value1
                    map_value = YamlNodeMakers.new_mapping_value_node(
                        ctx,
                        check.not_none(colon_tk),
                        entry_tk,
                        key0,
                        value1,
                    )
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)
                    ctx.go_next()

                else:
                    ctx.go_next()
                    if ctx.is_token_not_found():
                        return YamlSyntaxError('could not find map value', YamlParseToken.raw_token(colon_tk))
                    value2 = self.parse_token(ctx, ctx.current_token())
                    if isinstance(value2, YamlError):
                        return value2
                    map_value = YamlNodeMakers.new_mapping_value_node(
                        ctx,
                        check.not_none(colon_tk),
                        entry_tk,
                        key0,
                        value2,
                    )
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)

            else:
                if not self.is_flow_map_delim(check.not_none(ctx.next_token())):
                    err_tk = map_key_tk
                    if err_tk is None:
                        err_tk = tk
                    return YamlSyntaxError('could not find flow map content', YamlParseToken.raw_token(err_tk))

                key1 = self.parse_scalar_value(ctx, map_key_tk)
                if isinstance(key1, YamlError):
                    return key1

                value3 = YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(check.not_none(map_key_tk)))
                if isinstance(value3, YamlError):
                    return value3

                map_value = YamlNodeMakers.new_mapping_value_node(
                    ctx,
                    check.not_none(map_key_tk),
                    entry_tk,
                    check.not_none(key1),
                    value3,
                )
                if isinstance(map_value, YamlError):
                    return map_value

                node.values.append(map_value)
                ctx.go_next()

            is_first = False

        if node.end is None:
            return YamlSyntaxError("could not find flow mapping end token '}'", node.start)

        # set line comment if exists. e.g.) } # comment
        if (err := yaml_set_line_comment(ctx, node, ctx.current_token())) is not None:
            return err

        ctx.go_next()  # skip mapping end token.
        return node

    def is_flow_map_delim(self, tk: YamlParseToken) -> bool:
        return tk.type() == YamlTokenType.MAPPING_END or tk.type() == YamlTokenType.COLLECT_ENTRY

    def parse_map(self, ctx: YamlParsingContext) -> YamlErrorOr[MappingYamlNode]:
        key_tk = check.not_none(ctx.current_token())
        if key_tk.group is None:
            return YamlSyntaxError('unexpected map key', YamlParseToken.raw_token(key_tk))

        key_value_node: MappingValueYamlNode
        if YamlParseToken.group_type(key_tk) == YamlParseTokenGroupType.MAP_KEY_VALUE:
            node0 = self.parse_map_key_value(
                ctx.with_group(check.not_none(key_tk.group)),
                check.not_none(key_tk.group),
                None,
            )
            if isinstance(node0, YamlError):
                return node0

            key_value_node = node0
            ctx.go_next()
            if (err := self.validate_map_key_value_next_token(ctx, key_tk, ctx.current_token())) is not None:
                return err

        else:
            key = self.parse_map_key(ctx.with_group(check.not_none(key_tk.group)), check.not_none(key_tk.group))
            if isinstance(key, YamlError):
                return key
            ctx.go_next()

            value_tk = ctx.current_token()
            if (
                    YamlParseToken.line(key_tk) == YamlParseToken.line(value_tk) and
                    YamlParseToken.type(value_tk) == YamlTokenType.SEQUENCE_ENTRY
            ):
                return YamlSyntaxError(
                    'block sequence entries are not allowed in this context',
                    YamlParseToken.raw_token(value_tk),
                )

            ctx = ctx.with_child(self.map_key_text(key))
            value = self.parse_map_value(ctx, key, check.not_none(check.not_none(key_tk.group).last()))
            if isinstance(value, YamlError):
                return value

            node1 = YamlNodeMakers.new_mapping_value_node(
                ctx,
                check.not_none(check.not_none(key_tk.group).last()),
                None,
                key,
                value,
            )
            if isinstance(node1, YamlError):
                return node1

            key_value_node = node1

        map_node = YamlNodeMakers.new_mapping_node(
            ctx,
            YamlParseToken(token=key_value_node.get_token()),
            False,
            key_value_node,
        )
        if isinstance(map_node, YamlError):
            return map_node

        tk: ta.Optional[YamlParseToken]
        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        else:
            tk = ctx.current_token()

        while YamlParseToken.column(tk) == YamlParseToken.column(key_tk):
            typ = YamlParseToken.type(tk)
            if ctx.is_flow and typ == YamlTokenType.SEQUENCE_END:
                # [
                # key: value
                # ] <=
                break
            if not self.is_map_token(check.not_none(tk)):
                return YamlSyntaxError('non-map value is specified', YamlParseToken.raw_token(tk))
            cm = self.parse_head_comment(ctx)
            if typ == YamlTokenType.MAPPING_END:
                # a: {
                #  b: c
                # } <=
                ctx.go_next()
                break
            node2 = self.parse_map(ctx)
            if isinstance(node2, YamlError):
                return node2
            if len(node2.values) != 0:
                if (err := yaml_set_head_comment(cm, node2.values[0])) is not None:
                    return err
            map_node.values.extend(node2.values)
            if node2.foot_comment is not None:
                map_node.values[len(map_node.values) - 1].foot_comment = node2.foot_comment
            tk = ctx.current_token()

        if ctx.is_comment():
            if YamlParseToken.column(key_tk) <= YamlParseToken.column(ctx.current_token()):
                # If the comment is in the same or deeper column as the last element column in map value,
                # treat it as a footer comment for the last element.
                if len(map_node.values) == 1:
                    map_node.values[0].foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(key_tk))
                    BaseYamlNode.set_path(map_node.values[0].foot_comment, map_node.values[0].key.get_path())
                else:
                    map_node.foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(key_tk))
                    BaseYamlNode.set_path(map_node.foot_comment, map_node.get_path())

        return map_node

    def validate_map_key_value_next_token(self, ctx: YamlParsingContext, key_tk, tk: ta.Optional[YamlParseToken]) -> ta.Optional[YamlError]:  # noqa
        if tk is None:
            return None
        if tk.column() <= key_tk.column():
            return None
        if ctx.is_comment():
            return None
        if (
                ctx.is_flow and
                (tk.type() == YamlTokenType.COLLECT_ENTRY or tk.type() == YamlTokenType.SEQUENCE_END)
        ):
            return None
        # a: b
        #  c <= this token is invalid.
        return YamlSyntaxError('value is not allowed in this context. map key-value is pre-defined', tk.raw_token())

    def is_map_token(self, tk: YamlParseToken) -> bool:
        if tk.group is None:
            return tk.type() == YamlTokenType.MAPPING_START or tk.type() == YamlTokenType.MAPPING_END
        g = tk.group
        return g.type == YamlParseTokenGroupType.MAP_KEY or g.type == YamlParseTokenGroupType.MAP_KEY_VALUE

    def parse_map_key_value(
            self,
            ctx: YamlParsingContext,
            g: YamlParseTokenGroup,
            entry_tk: ta.Optional[YamlParseToken],
    ) -> YamlErrorOr[MappingValueYamlNode]:
        if g.type != YamlParseTokenGroupType.MAP_KEY_VALUE:
            return YamlSyntaxError('unexpected map key-value pair', g.raw_token())
        if check.not_none(g.first()).group is None:
            return YamlSyntaxError('unexpected map key', g.raw_token())
        key_group = check.not_none(check.not_none(g.first()).group)
        key = self.parse_map_key(ctx.with_group(key_group), key_group)
        if isinstance(key, YamlError):
            return key

        c = ctx.with_child(self.map_key_text(key))
        value = self.parse_token(c, g.last())
        if isinstance(value, YamlError):
            return value
        return YamlNodeMakers.new_mapping_value_node(c, check.not_none(key_group.last()), entry_tk, key, value)

    def parse_map_key(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[MapKeyYamlNode]:
        if g.type != YamlParseTokenGroupType.MAP_KEY:
            return YamlSyntaxError('unexpected map key', g.raw_token())

        if YamlParseToken.type(g.first()) == YamlTokenType.MAPPING_KEY:
            map_key_tk = check.not_none(g.first())
            if map_key_tk.group is not None:
                ctx = ctx.with_group(map_key_tk.group)
            key0 = YamlNodeMakers.new_mapping_key_node(ctx, map_key_tk)
            if isinstance(key0, YamlError):
                return key0
            ctx.go_next()  # skip mapping key token
            if ctx.is_token_not_found():
                return YamlSyntaxError('could not find value for mapping key', YamlParseToken.raw_token(map_key_tk))

            scalar0 = self.parse_scalar_value(ctx, ctx.current_token())
            if isinstance(scalar0, YamlError):
                return scalar0
            key0.value = scalar0
            key_text = self.map_key_text(scalar0)
            key_path = ctx.with_child(key_text).path
            key0.set_path(key_path)
            if (err := self.validate_map_key(
                    ctx,
                    check.not_none(key0.get_token()),
                    key_path,
                    check.not_none(g.last()),
            )) is not None:
                return err
            self.path_map[key_path] = key0
            return key0
        if YamlParseToken.type(g.last()) != YamlTokenType.MAPPING_VALUE:
            return YamlSyntaxError("expected map key-value delimiter ':'", YamlParseToken.raw_token(g.last()))

        scalar1 = self.parse_scalar_value(ctx, g.first())
        if isinstance(scalar1, YamlError):
            return scalar1
        if not isinstance(scalar1, MapKeyYamlNode):
            # FIXME: not possible
            return YamlSyntaxError(
                'cannot take map-key node',
                check.not_none(scalar1).get_token(),
            )
        key1: MapKeyYamlNode = ta.cast(MapKeyYamlNode, scalar1)
        key_text = self.map_key_text(key1)
        key_path = ctx.with_child(key_text).path
        key1.set_path(key_path)
        if (err := self.validate_map_key(
                ctx,
                check.not_none(key1.get_token()),
                key_path,
                check.not_none(g.last()),
        )) is not None:
            return err
        self.path_map[key_path] = key1
        return key1

    def validate_map_key(
            self,
            ctx: YamlParsingContext,
            tk: YamlToken,
            key_path: str,
            colon_tk: YamlParseToken,
    ) -> ta.Optional[YamlError]:
        if not self.allow_duplicate_map_key:
            if (n := self.path_map.get(key_path)) is not None:
                pos = check.not_none(n.get_token()).position
                return YamlSyntaxError(
                    f'mapping key {tk.value!r} already defined at [{pos.line:d}:{pos.column:d}]',
                    tk,
                )
        origin = self.remove_left_white_space(tk.origin)
        if ctx.is_flow:
            if tk.type == YamlTokenType.STRING:
                origin = self.remove_right_white_space(origin)
                if tk.position.line + self.new_line_character_num(origin) != colon_tk.line():
                    return YamlSyntaxError('map key definition includes an implicit line break', tk)
            return None
        if (
                tk.type != YamlTokenType.STRING and
                tk.type != YamlTokenType.SINGLE_QUOTE and
                tk.type != YamlTokenType.DOUBLE_QUOTE
        ):
            return None
        if self.exists_new_line_character(origin):
            return YamlSyntaxError('unexpected key name', tk)
        return None

    def remove_left_white_space(self, src: str) -> str:
        # CR or LF or CRLF
        return src.lstrip(' \r\n')

    def remove_right_white_space(self, src: str) -> str:
        # CR or LF or CRLF
        return src.rstrip(' \r\n')

    def exists_new_line_character(self, src: str) -> bool:
        return self.new_line_character_num(src) > 0

    def new_line_character_num(self, src: str) -> int:
        num = 0
        i = -1
        while True:
            i += 1
            if not (i < len(src)):
                break
            if src[i] == '\r':
                if len(src) > i + 1 and src[i + 1] == '\n':
                    i += 1
                num += 1
            elif src[i] == '\n':
                num += 1
        return num

    def map_key_text(self, n: ta.Optional[YamlNode]) -> str:
        if n is None:
            return ''
        nn = n
        if isinstance(nn, MappingKeyYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, TagYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, AnchorYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, AliasYamlNode):
            return ''
        return check.not_none(n.get_token()).value

    def parse_map_value(
            self,
            ctx: YamlParsingContext,
            key: MapKeyYamlNode,
            colon_tk: YamlParseToken,
    ) -> YamlErrorOr[YamlNode]:
        tk = ctx.current_token()
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.add_null_value_token(colon_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        key_col = check.not_none(key.get_token()).position.column
        key_line = check.not_none(key.get_token()).position.line

        if (
            YamlParseToken.column(tk) != key_col and
            YamlParseToken.line(tk) == key_line and
            (
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.MAP_KEY or
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.MAP_KEY_VALUE
            )
        ):
            # a: b:
            #    ^
            #
            # a: b: c
            #    ^
            return YamlSyntaxError('mapping value is not allowed in this context', YamlParseToken.raw_token(tk))

        if YamlParseToken.column(tk) == key_col and self.is_map_token(check.not_none(tk)):
            # in this case,
            # ----
            # key: <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                YamlParseToken.line(tk) == key_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) == key_col and
                self.is_map_token(check.not_none(ctx.next_token()))
        ):
            # in this case,
            # ----
            # key: &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if (
                YamlParseToken.column(tk) <= key_col and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME
        ):
            # key: <value does not defined>
            # &anchor
            return YamlSyntaxError('anchor is not allowed in this context', YamlParseToken.raw_token(tk))
        if YamlParseToken.column(tk) <= key_col and YamlParseToken.type(tk) == YamlTokenType.TAG:
            # key: <value does not defined>
            # !!tag
            return YamlSyntaxError('tag is not allowed in this context', YamlParseToken.raw_token(tk))

        if YamlParseToken.column(tk) < key_col:
            # in this case,
            # ----
            #   key: <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                YamlParseToken.line(tk) == key_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) < key_col
        ):
            # in this case,
            # ----
            #   key: &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if (err := self.validate_anchor_value_in_map_or_seq(value, key_col)) is not None:
            return err
        return value

    def validate_anchor_value_in_map_or_seq(self, value: YamlNode, col: int) -> ta.Optional[YamlError]:
        if not isinstance(value, AnchorYamlNode):
            return None
        anchor: AnchorYamlNode = value
        if not isinstance(anchor.value, TagYamlNode):
            return None
        tag: TagYamlNode = anchor.value
        anchor_tk = anchor.get_token()
        tag_tk = tag.get_token()

        if anchor_tk.position.line == tag_tk.position.line:
            # key:
            #   &anchor !!tag
            #
            # - &anchor !!tag
            return None

        if tag_tk.position.column <= col:
            # key: &anchor
            # !!tag
            #
            # - &anchor
            # !!tag
            return YamlSyntaxError('tag is not allowed in this context', tag_tk)
        return None

    def parse_anchor(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[AnchorYamlNode]:
        anchor_name_group = check.not_none(check.not_none(g.first()).group)
        anchor = self.parse_anchor_name(ctx.with_group(anchor_name_group))
        if isinstance(anchor, YamlError):
            return anchor
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find anchor value', anchor.get_token())

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if isinstance(value, AnchorYamlNode):
            return YamlSyntaxError('anchors cannot be used consecutively', value.get_token())
        anchor.value = value
        return anchor

    def parse_anchor_name(self, ctx: YamlParsingContext) -> YamlErrorOr[AnchorYamlNode]:
        anchor = YamlNodeMakers.new_anchor_node(ctx, ctx.current_token())
        if isinstance(anchor, YamlError):
            return anchor
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find anchor value', anchor.get_token())

        anchor_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(anchor_name, YamlError):
            return anchor_name
        if anchor_name is None:
            return YamlSyntaxError(
                'unexpected anchor. anchor name is not scalar value',
                YamlParseToken.raw_token(ctx.current_token()),
            )
        anchor.name = anchor_name
        return anchor

    def parse_alias(self, ctx: YamlParsingContext) -> YamlErrorOr[AliasYamlNode]:
        alias = YamlNodeMakers.new_alias_node(ctx, ctx.current_token())
        if isinstance(alias, YamlError):
            return alias
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find alias value', alias.get_token())

        alias_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(alias_name, YamlError):
            return alias_name
        if alias_name is None:
            return YamlSyntaxError(
                'unexpected alias. alias name is not scalar value',
                YamlParseToken.raw_token(ctx.current_token()),
            )
        alias.value = alias_name
        return alias

    def parse_literal(self, ctx: YamlParsingContext) -> YamlErrorOr[LiteralYamlNode]:
        node = YamlNodeMakers.new_literal_node(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip literal/folded token

        tk = ctx.current_token()
        if tk is None:
            value0 = YamlNodeMakers.new_string_node(
                ctx,
                YamlParseToken(token=yaml_new_token('', '', node.start.position)),
            )
            if isinstance(value0, YamlError):
                return value0
            node.value = value0
            return node
        value1 = self.parse_token(ctx, tk)
        if isinstance(value1, YamlError):
            return value1
        if not isinstance(s := value1, StringYamlNode):
            return YamlSyntaxError('unexpected token. required string token', value1.get_token())
        node.value = s
        return node

    def parse_scalar_tag(self, ctx: YamlParsingContext) -> YamlErrorOr[TagYamlNode]:
        tag = self.parse_tag(ctx)
        if isinstance(tag, YamlError):
            return tag
        if tag.value is None:
            return YamlSyntaxError('specified not scalar tag', tag.get_token())
        if not isinstance(tag.value, ScalarYamlNode):
            return YamlSyntaxError('specified not scalar tag', tag.get_token())
        return tag

    def parse_tag(self, ctx: YamlParsingContext) -> YamlErrorOr[TagYamlNode]:
        tag_tk = ctx.current_token()
        tag_raw_tk = YamlParseToken.raw_token(tag_tk)
        node = YamlNodeMakers.new_tag_node(ctx, tag_tk)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()

        comment = self.parse_head_comment(ctx)

        tag_value: YamlNode
        if self.secondary_tag_directive is not None:
            value0 = YamlNodeMakers.new_string_node(ctx, ctx.current_token())
            if isinstance(value0, YamlError):
                return value0
            tag_value = value0
            node.directive = self.secondary_tag_directive
        else:
            value1 = self.parse_tag_value(ctx, check.not_none(tag_raw_tk), ctx.current_token())
            if isinstance(value1, YamlError):
                return value1
            tag_value = check.not_none(value1)
        if (err := yaml_set_head_comment(comment, tag_value)) is not None:
            return err
        node.value = tag_value
        return node

    def parse_tag_value(
            self,
            ctx: YamlParsingContext,
            tag_raw_tk: YamlToken,
            tk: ta.Optional[YamlParseToken],
    ) -> YamlErrorOr[ta.Optional[YamlNode]]:
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.create_implicit_null_token(YamlParseToken(token=tag_raw_tk)))
        if tag_raw_tk.value in (
                YamlReservedTagKeywords.MAPPING,
                YamlReservedTagKeywords.SET,
        ):
            if not self.is_map_token(tk):
                return YamlSyntaxError('could not find map', tk.raw_token())
            if tk.type() == YamlTokenType.MAPPING_START:
                return self.parse_flow_map(ctx.with_flow(True))
            return self.parse_map(ctx)
        elif tag_raw_tk.value in (
                YamlReservedTagKeywords.INTEGER,
                YamlReservedTagKeywords.FLOAT,
                YamlReservedTagKeywords.STRING,
                YamlReservedTagKeywords.BINARY,
                YamlReservedTagKeywords.TIMESTAMP,
                YamlReservedTagKeywords.BOOLEAN,
                YamlReservedTagKeywords.NULL,
        ):
            if tk.group_type() == YamlParseTokenGroupType.LITERAL or tk.group_type() == YamlParseTokenGroupType.FOLDED:
                return self.parse_literal(ctx.with_group(check.not_none(tk.group)))
            elif tk.type() == YamlTokenType.COLLECT_ENTRY or tk.type() == YamlTokenType.MAPPING_VALUE:
                return YamlNodeMakers.new_tag_default_scalar_value_node(ctx, tag_raw_tk)
            scalar = self.parse_scalar_value(ctx, tk)
            if isinstance(scalar, YamlError):
                return scalar
            ctx.go_next()
            return scalar
        elif tag_raw_tk.value in (
                YamlReservedTagKeywords.SEQUENCE,
                YamlReservedTagKeywords.ORDERED_MAP,
        ):
            if tk.type() == YamlTokenType.SEQUENCE_START:
                return self.parse_flow_sequence(ctx.with_flow(True))
            return self.parse_sequence(ctx)
        return self.parse_token(ctx, tk)

    def parse_flow_sequence(self, ctx: YamlParsingContext) -> YamlErrorOr[SequenceYamlNode]:
        node = YamlNodeMakers.new_sequence_node(ctx, ctx.current_token(), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip SequenceStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_END:
                node.end = YamlParseToken.raw_token(tk)
                break

            entry_tk: ta.Optional[YamlParseToken] = None
            if YamlParseToken.type(tk) == YamlTokenType.COLLECT_ENTRY:
                if is_first:
                    return YamlSyntaxError("expected sequence element, but found ','", YamlParseToken.raw_token(tk))
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return YamlSyntaxError("',' or ']' must be specified", YamlParseToken.raw_token(tk))

            if YamlParseToken.type(tk := ctx.current_token()) == YamlTokenType.SEQUENCE_END:
                # this case is here: "[ elem, ]".
                # In this case, ignore the last element and break sequence parsing.
                node.end = YamlParseToken.raw_token(tk)
                break

            if ctx.is_token_not_found():
                break

            ctx = ctx.with_index(len(node.values))
            value = self.parse_token(ctx, ctx.current_token())
            if isinstance(value, YamlError):
                return value
            node.values.append(value)
            seq_entry = yaml_sequence_entry(
                entry_tk.raw_token() if entry_tk is not None else None,
                value,
                None,
            )
            if (err := yaml_set_line_comment(ctx, seq_entry, entry_tk)) is not None:
                return err
            seq_entry.set_path(ctx.path)
            node.entries.append(seq_entry)

            is_first = False
        if node.end is None:
            return YamlSyntaxError("sequence end token ']' not found", node.start)

        # set ine comment if exists. e.g.) ] # comment
        if (err := yaml_set_line_comment(ctx, node, ctx.current_token())) is not None:
            return err
        ctx.go_next()  # skip sequence end token.
        return node

    def parse_sequence(self, ctx: YamlParsingContext) -> YamlErrorOr[SequenceYamlNode]:
        seq_tk = ctx.current_token()
        seq_node = YamlNodeMakers.new_sequence_node(ctx, seq_tk, False)
        if isinstance(seq_node, YamlError):
            return seq_node

        tk = seq_tk
        while (
                YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY and
                YamlParseToken.column(tk) == YamlParseToken.column(seq_tk)
        ):
            head_comment = self.parse_head_comment(ctx)
            ctx.go_next()  # skip sequence entry token

            ctx = ctx.with_index(len(seq_node.values))
            value = self.parse_sequence_value(ctx, check.not_none(seq_tk))
            if isinstance(value, YamlError):
                return value
            seq_entry = yaml_sequence_entry(YamlParseToken.raw_token(seq_tk), value, head_comment)
            if (err := yaml_set_line_comment(ctx, seq_entry, seq_tk)) is not None:
                return err
            seq_entry.set_path(ctx.path)
            seq_node.value_head_comments.append(head_comment)
            seq_node.values.append(value)
            seq_node.entries.append(seq_entry)

            if ctx.is_comment():
                tk = ctx.next_not_comment_token()
            else:
                tk = ctx.current_token()
        if ctx.is_comment():
            if YamlParseToken.column(seq_tk) <= YamlParseToken.column(ctx.current_token()):
                # If the comment is in the same or deeper column as the last element column in sequence value,
                # treat it as a footer comment for the last element.
                seq_node.foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(seq_tk))
                if len(seq_node.values) != 0:
                    check.not_none(seq_node.foot_comment).set_path(
                        check.not_none(seq_node.values[len(seq_node.values) - 1]).get_path(),
                    )
        return seq_node

    def parse_sequence_value(self, ctx: YamlParsingContext, seq_tk: YamlParseToken) -> YamlErrorOr[YamlNode]:
        tk = ctx.current_token()
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.add_null_value_token(seq_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        seq_col = seq_tk.column()
        seq_line = seq_tk.line()

        if YamlParseToken.column(tk) == seq_col and YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY:
            # in this case,
            # ----
            # - <value does not defined>
            # -
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                YamlParseToken.line(tk) == seq_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) == seq_col and
                YamlParseToken.type(ctx.next_token()) == YamlTokenType.SEQUENCE_ENTRY
        ):
            # in this case,
            # ----
            # - &anchor
            # -
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if (
                YamlParseToken.column(tk) <= seq_col and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME
        ):
            # - <value does not defined>
            # &anchor
            return YamlSyntaxError('anchor is not allowed in this sequence context', YamlParseToken.raw_token(tk))
        if YamlParseToken.column(tk) <= seq_col and YamlParseToken.type(tk) == YamlTokenType.TAG:
            # - <value does not defined>
            # !!tag
            return YamlSyntaxError('tag is not allowed in this sequence context', YamlParseToken.raw_token(tk))

        if (
                YamlParseToken.column(tk) < seq_col or
                (YamlParseToken.column(tk) == seq_col and YamlParseToken.line(tk) != seq_line)
        ):
            # in this case,
            # ----
            #   - <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                YamlParseToken.line(tk) == seq_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) < seq_col
        ):
            # in this case,
            # ----
            #   - &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if (err := self.validate_anchor_value_in_map_or_seq(value, seq_col)) is not None:
            return err
        return value

    def parse_directive(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[DirectiveYamlNode]:
        directive_name_group = check.not_none(check.not_none(g.first()).group)
        directive = self.parse_directive_name(ctx.with_group(directive_name_group))
        if isinstance(directive, YamlError):
            return directive

        if directive.name == 'YAML':
            if len(g.tokens) != 2:
                return YamlSyntaxError('unexpected format YAML directive', YamlParseToken.raw_token(g.first()))
            value_tk = g.tokens[1]
            value_raw_tk = check.not_none(value_tk.raw_token())
            value0 = value_raw_tk.value
            ver = YAML_VERSION_MAP.get(value0)
            if ver is None:
                return YamlSyntaxError(f'unknown YAML version {value0!r}', value_raw_tk)
            if self.yaml_version != '':
                return YamlSyntaxError('YAML version has already been specified', value_raw_tk)
            self.yaml_version = ver
            version_node = YamlNodeMakers.new_string_node(ctx, value_tk)
            if isinstance(version_node, YamlError):
                return version_node
            directive.values.append(version_node)

        elif directive.name == 'TAG':
            if len(g.tokens) != 3:
                return YamlSyntaxError('unexpected format TAG directive', YamlParseToken.raw_token(g.first()))
            tag_key = YamlNodeMakers.new_string_node(ctx, g.tokens[1])
            if isinstance(tag_key, YamlError):
                return tag_key
            if tag_key.value == '!!':
                self.secondary_tag_directive = directive
            tag_value = YamlNodeMakers.new_string_node(ctx, g.tokens[2])
            if isinstance(tag_value, YamlError):
                return tag_value
            directive.values.extend([tag_key, tag_value])

        elif len(g.tokens) > 1:
            for tk in g.tokens[1:]:
                value1 = YamlNodeMakers.new_string_node(ctx, tk)
                if isinstance(value1, YamlError):
                    return value1
                directive.values.append(value1)

        return directive

    def parse_directive_name(self, ctx: YamlParsingContext) -> YamlErrorOr[DirectiveYamlNode]:
        directive = YamlNodeMakers.new_directive_node(ctx, ctx.current_token())
        if isinstance(directive, YamlError):
            return directive
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find directive value', directive.get_token())

        directive_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(directive_name, YamlError):
            return directive_name
        if directive_name is None:
            return YamlSyntaxError(
                'unexpected directive. directive name is not scalar value',
                YamlParseToken.raw_token(ctx.current_token()),
            )
        directive.name = directive_name
        return directive

    def parse_comment(self, ctx: YamlParsingContext) -> YamlErrorOr[ta.Optional[YamlNode]]:
        cm = self.parse_head_comment(ctx)
        if ctx.is_token_not_found():
            return cm
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if (err := yaml_set_head_comment(cm, node)) is not None:
            return err
        return node

    def parse_head_comment(self, ctx: YamlParsingContext) -> ta.Optional[CommentGroupYamlNode]:
        tks: ta.List[ta.Optional[YamlToken]] = []
        while ctx.is_comment():
            tks.append(YamlParseToken.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return YamlAsts.comment_group(tks)

    def parse_foot_comment(self, ctx: YamlParsingContext, col: int) -> ta.Optional[CommentGroupYamlNode]:
        tks: ta.List[ta.Optional[YamlToken]] = []
        while ctx.is_comment() and col <= YamlParseToken.column(ctx.current_token()):
            tks.append(YamlParseToken.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return YamlAsts.comment_group(tks)


########################################
# ../decoding.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


class YamlDecodeContext:
    def __init__(self, values: ta.Optional[ta.Dict[ta.Any, ta.Any]] = None) -> None:
        super().__init__()

        self._values: ta.Dict[ta.Any, ta.Any] = values if values is not None else {}

    def with_value(self, key: ta.Any, value: ta.Any) -> 'YamlDecodeContext':
        return YamlDecodeContext({**self._values, key: value})

    def value(self, key: ta.Any) -> ta.Any:
        return self._values.get(key)

    #

    class _MergeKey:  # noqa
        pass

    def with_merge(self) -> 'YamlDecodeContext':
        return self.with_value(self._MergeKey, True)

    def is_merge(self) -> bool:
        if not isinstance(v := self.value(self._MergeKey), bool):
            return False

        return v

    #

    class _AnchorKey:  # noqa
        pass

    def with_anchor(self, name: str) -> 'YamlDecodeContext':
        anchor_map = self.get_anchor_map()
        new_map: ta.Dict[str, None] = {}
        new_map.update(anchor_map)
        new_map[name] = None
        return self.with_value(self._AnchorKey, new_map)

    def get_anchor_map(self) -> ta.Dict[str, None]:
        if not isinstance(v := self.value(self._AnchorKey), dict):
            return {}

        return v


##


# CommentPosition type of the position for comment.
class YamlCommentPosition(enum.IntEnum):
    HEAD = 0
    LINE = 1
    FOOT = 2


# Comment raw data for comment.
@dc.dataclass()
class YamlComment:
    texts: ta.List[str]
    position: YamlCommentPosition


# LineComment create a one-line comment for CommentMap.
def yaml_line_comment(text: str) -> YamlComment:
    return YamlComment(
        texts=[text],
        position=YamlCommentPosition.LINE,
    )


# HeadComment create a multiline comment for CommentMap.
def yaml_head_comment(*texts: str) -> YamlComment:
    return YamlComment(
        texts=list(texts),
        position=YamlCommentPosition.HEAD,
    )


# FootComment create a multiline comment for CommentMap.
def yaml_foot_comment(*texts: str) -> YamlComment:
    return YamlComment(
        texts=list(texts),
        position=YamlCommentPosition.FOOT,
    )


# CommentMap map of the position of the comment and the comment information.
class YamlCommentMap(ta.Dict[str, ta.List[YamlComment]]):
    pass


##


# MapItem is an item in a MapSlice.
@dc.dataclass()
class YamlMapItem:
    key: ta.Any
    value: ta.Any


# MapSlice encodes and decodes as a YAML map.
# The order of keys is preserved when encoding and decoding.
class YamlMapSlice(ta.List[YamlMapItem]):
    # ToMap convert to map[interface{}]interface{}.
    def to_map(self) -> ta.Dict[ta.Any, ta.Any]:
        return {item.key: item.value for item in self}


##


class YamlBytesReader(ta.Protocol):
    def read(self) -> bytes: ...


class ImmediateYamlBytesReader:
    def __init__(self, bs: bytes) -> None:
        self._bs = bs

    def read(self) -> bytes:
        bs = self._bs
        self._bs = b''
        return bs


##


class YamlDecodeOption(ta.Protocol):
    def __call__(self, d: 'YamlDecoder') -> ta.Optional[YamlError]: ...


##


class YamlDecodeErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    EXCEEDED_MAX_DEPTH = yaml_error('exceeded max depth')


@dc.dataclass()
class DuplicateKeyYamlError(YamlError):
    msg: str
    token: YamlToken

    @property
    def message(self) -> str:
        return self.msg


##


# Decoder reads and decodes YAML values from an input stream.
class YamlDecoder:
    reader: YamlBytesReader
    reference_readers: ta.List[YamlBytesReader]
    anchor_node_map: ta.Dict[str, ta.Optional[YamlNode]]
    anchor_value_map: ta.Dict[str, ta.Any]
    comment_maps: ta.List[YamlCommentMap]
    to_comment_map: ta.Optional[YamlCommentMap] = None
    opts: ta.List[YamlDecodeOption]
    reference_files: ta.List[str]
    reference_dirs: ta.List[str]
    is_recursive_dir: bool = False
    is_resolved_reference: bool = False
    allow_duplicate_map_key: bool = False
    use_ordered_map: bool = False
    parsed_file: ta.Optional[YamlFile] = None
    stream_index: int = 0
    decode_depth: int = 0

    # NewDecoder returns a new decoder that reads from r.
    def __init__(self, r: YamlBytesReader, *opts: YamlDecodeOption) -> None:
        super().__init__()

        self.reader = r
        self.anchor_node_map = {}
        self.anchor_value_map = {}
        self.opts = list(opts)
        self.reference_readers = []
        self.reference_files = []
        self.reference_dirs = []
        self.is_recursive_dir = False
        self.is_resolved_reference = False
        self.allow_duplicate_map_key = False
        self.use_ordered_map = False

        self.comment_maps = []

    MAX_DECODE_DEPTH: ta.ClassVar[int] = 10000

    def step_in(self) -> None:
        self.decode_depth += 1

    def step_out(self) -> None:
        self.decode_depth -= 1

    def is_exceeded_max_depth(self) -> bool:
        return self.decode_depth > self.MAX_DECODE_DEPTH

    def cast_to_float(self, v: ta.Any) -> ta.Any:
        if isinstance(v, float):
            return v
        elif isinstance(v, int):
            return float(v)
        elif isinstance(v, str):
            # if error occurred, return zero value
            try:
                return float(v)
            except ValueError:
                return 0
        return 0

    def map_key_node_to_string(self, ctx: YamlDecodeContext, node: MapKeyYamlNode) -> YamlErrorOr[str]:
        key = self.node_to_value(ctx, node)
        if isinstance(key, YamlError):
            return key
        if key is None:
            return 'null'
        if isinstance(key, str):
            return key
        return str(key)

    def set_to_map_value(
            self,
            ctx: YamlDecodeContext,
            node: YamlNode,
            m: ta.Dict[str, ta.Any],
    ) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)
            if isinstance(n := node, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(n.value, True)
                    if isinstance(value, YamlError):
                        return value

                    it = value.map_range()
                    while it.next():
                        if (err := self.set_to_map_value(ctx, it.key_value(), m)) is not None:
                            return err

                else:
                    key = self.map_key_node_to_string(ctx, n.key)
                    if isinstance(key, YamlError):
                        return key

                    v = self.node_to_value(ctx, n.value)
                    if isinstance(v, YamlError):
                        return v

                    m[key] = v

            elif isinstance(n, MappingYamlNode):
                for value2 in n.values:
                    if (err := self.set_to_map_value(ctx, value2, m)) is not None:
                        return err

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value
                self.anchor_node_map[anchor_name] = n.value

            return None

        finally:
            self.step_out()

    def set_to_ordered_map_value(
            self,
            ctx: YamlDecodeContext,
            node: YamlNode,
            m: YamlMapSlice,
    ) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)
            if isinstance(n := node, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(n.value, True)
                    if isinstance(value, YamlError):
                        return value

                    it = value.map_range()
                    while it.next():
                        if (err := self.set_to_ordered_map_value(ctx, it.key_value(), m)) is not None:
                            return err

                else:
                    key = self.map_key_node_to_string(ctx, n.key)
                    if isinstance(key, YamlError):
                        return key

                    value = self.node_to_value(ctx, n.value)
                    if isinstance(value, YamlError):
                        return value

                    m.append(YamlMapItem(key, value))

            elif isinstance(n, MappingYamlNode):
                for value2 in n.values:
                    if (err := self.set_to_ordered_map_value(ctx, value2, m)) is not None:
                        return err

            return None

        finally:
            self.step_out()

    def set_path_comment_map(self, node: ta.Optional[YamlNode]) -> None:
        if node is None:
            return

        if self.to_comment_map is None:
            return

        self.add_head_or_line_comment_to_map(node)
        self.add_foot_comment_to_map(node)

    def add_head_or_line_comment_to_map(self, node: YamlNode) -> None:
        if isinstance(node, SequenceYamlNode):
            self.add_sequence_node_comment_to_map(node)
            return

        comment_group = node.get_comment()
        if comment_group is None:
            return

        texts: ta.List[str] = []
        target_line = check.not_none(node.get_token()).position.line
        min_comment_line = 1_000_000_000  # FIXME lol
        for comment in comment_group.comments:
            if min_comment_line > check.not_none(comment.token).position.line:
                min_comment_line = check.not_none(comment.token).position.line

            texts.append(check.not_none(comment.token).value)

        if len(texts) == 0:
            return

        comment_path = node.get_path()
        if min_comment_line < target_line:
            if isinstance(n := node, MappingYamlNode):
                if len(n.values) != 0:
                    comment_path = n.values[0].key.get_path()

            elif isinstance(n, MappingValueYamlNode):
                comment_path = n.key.get_path()

            self.add_comment_to_map(comment_path, yaml_head_comment(*texts))
        else:
            self.add_comment_to_map(comment_path, yaml_line_comment(texts[0]))

    def add_sequence_node_comment_to_map(self, node: SequenceYamlNode) -> None:
        if len(node.value_head_comments) != 0:
            for idx, hc in enumerate(node.value_head_comments):
                if hc is None:
                    continue

                texts: ta.List[str] = []
                for comment in hc.comments:
                    texts.append(check.not_none(comment.token).value)

                if len(texts) != 0:
                    self.add_comment_to_map(check.not_none(node.values[idx]).get_path(), yaml_head_comment(*texts))

        first_elem_head_comment = node.get_comment()
        if first_elem_head_comment is not None:
            texts = []
            for comment in first_elem_head_comment.comments:
                texts.append(check.not_none(comment.token).value)

            if len(texts) != 0:
                if len(node.values) != 0:
                    self.add_comment_to_map(check.not_none(node.values[0]).get_path(), yaml_head_comment(*texts))

    def add_foot_comment_to_map(self, node: YamlNode) -> None:
        fc: ta.Optional[CommentGroupYamlNode] = None
        foot_comment_path = node.get_path()

        if isinstance(n := node, SequenceYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        elif isinstance(n, MappingYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        elif isinstance(n, MappingValueYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        if fc is None:
            return

        texts: ta.List[str] = []
        for comment in fc.comments:
            texts.append(check.not_none(comment.token).value)

        if len(texts) != 0:
            self.add_comment_to_map(foot_comment_path, yaml_foot_comment(*texts))

    def add_comment_to_map(self, path: str, comment: YamlComment) -> None:
        tcm = check.not_none(self.to_comment_map)[path]
        for c in tcm:
            if c.position == comment.position:
                # already added same comment
                return

        tcm.append(comment)
        tcm.sort(key=lambda c: c.position)

    def node_to_value(self, ctx: YamlDecodeContext, node: YamlNode) -> YamlErrorOr[ta.Any]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)

            if isinstance(n := node, NullYamlNode):
                return None

            elif isinstance(n, StringYamlNode):
                return n.get_value()

            elif isinstance(n, IntegerYamlNode):
                return n.get_value()

            elif isinstance(n, FloatYamlNode):
                return n.get_value()

            elif isinstance(n, BoolYamlNode):
                return n.get_value()

            elif isinstance(n, InfinityYamlNode):
                return n.get_value()

            elif isinstance(n, NanYamlNode):
                return n.get_value()

            elif isinstance(n, TagYamlNode):
                if n.directive is not None:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if v is None:
                        return ''

                    return str(v)

                rtk = n.start.value
                if rtk == YamlReservedTagKeywords.TIMESTAMP:
                    t = self.cast_to_time(ctx, check.not_none(n.value))
                    if isinstance(t, YamlError):
                        return None
                    return t

                elif rtk == YamlReservedTagKeywords.INTEGER:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    try:
                        return int(str(v))
                    except ValueError:
                        return 0

                elif rtk == YamlReservedTagKeywords.FLOAT:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    return self.cast_to_float(v)

                elif rtk == YamlReservedTagKeywords.NULL:
                    return None

                elif rtk == YamlReservedTagKeywords.BINARY:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if not isinstance(v, str):
                        return YamlSyntaxError(
                            f'cannot convert {str(v)!r} to string',
                            check.not_none(check.not_none(n.value).get_token()),
                        )
                    try:
                        return base64.b64decode(v)
                    except ValueError:
                        return None

                elif rtk == YamlReservedTagKeywords.BOOLEAN:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    l = str(v).lower()
                    if l in ('true', 't', '1', 'yes'):
                        return True
                    if l in ('false', 'f', '0', 'no'):
                        return False
                    return YamlSyntaxError(
                        f'cannot convert {v!r} to boolean',
                        check.not_none(check.not_none(n.value).get_token()),
                    )

                elif rtk == YamlReservedTagKeywords.STRING:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if v is None:
                        return ''
                    return str(v)

                elif rtk == YamlReservedTagKeywords.MAPPING:
                    return self.node_to_value(ctx, check.not_none(n.value))

                else:
                    return self.node_to_value(ctx, check.not_none(n.value))

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value

                # To handle the case where alias is processed recursively, the result of alias can be set to nil in
                # advance.
                self.anchor_node_map[anchor_name] = None
                anchor_value = self.node_to_value(ctx.with_anchor(anchor_name), check.not_none(n.value))
                if isinstance(anchor_value, YamlError):
                    del self.anchor_node_map[anchor_name]
                    return anchor_value
                self.anchor_node_map[anchor_name] = n.value
                self.anchor_value_map[anchor_name] = anchor_value
                return anchor_value

            elif isinstance(n, AliasYamlNode):
                text = check.not_none(n.value).string()
                if text in ctx.get_anchor_map():
                    # self recursion.
                    return None
                try:
                    v = self.anchor_value_map[text]
                except KeyError:
                    pass
                else:
                    return v
                try:
                    node2 = self.anchor_node_map[text]
                except KeyError:
                    pass
                else:
                    return self.node_to_value(ctx, check.not_none(node2))
                return YamlSyntaxError(
                    f'could not find alias {text!r}',
                    check.not_none(check.not_none(n.value).get_token()),
                )

            elif isinstance(n, LiteralYamlNode):
                return check.not_none(n.value).get_value()

            elif isinstance(n, MappingKeyYamlNode):
                return self.node_to_value(ctx, check.not_none(n.value))

            elif isinstance(n, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(check.not_none(n.value), True)
                    if isinstance(value, YamlError):
                        return value
                    it = value.map_range()
                    if self.use_ordered_map:
                        m = YamlMapSlice()
                        while it.next():
                            if (err := self.set_to_ordered_map_value(ctx, it.key_value(), m)) is not None:
                                return err
                        return m
                    m2: ta.Dict[str, ta.Any] = {}
                    while it.next():
                        if (err := self.set_to_map_value(ctx, it.key_value(), m2)) is not None:
                            return err
                    return m2

                key = self.map_key_node_to_string(ctx, n.key)
                if isinstance(key, YamlError):
                    return key

                if self.use_ordered_map:
                    v = self.node_to_value(ctx, n.value)
                    if isinstance(v, YamlError):
                        return v
                    return YamlMapSlice([YamlMapItem(key, v)])

                v = self.node_to_value(ctx, n.value)
                if isinstance(v, YamlError):
                    return v

                return {key: v}

            elif isinstance(n, MappingYamlNode):
                if self.use_ordered_map:
                    m3 = YamlMapSlice()
                    for value2 in n.values:
                        if (err := self.set_to_ordered_map_value(ctx, value2, m3)) is not None:
                            return err
                    return m3

                m4: ta.Dict[str, ta.Any] = {}
                for value3 in n.values:
                    if (err := self.set_to_map_value(ctx, value3, m4)) is not None:
                        return err
                return m4

            elif isinstance(n, SequenceYamlNode):
                v2: ta.List[ta.Any] = []
                for value4 in n.values:
                    vv = self.node_to_value(ctx, check.not_none(value4))
                    if isinstance(vv, YamlError):
                        return vv
                    v2.append(vv)
                return v2

            return None

        finally:
            self.step_out()

    def cast_to_time(self, ctx: YamlDecodeContext, src: YamlNode) -> YamlErrorOr[datetime.datetime]:
        raise NotImplementedError

    def get_map_node(self, node: YamlNode, is_merge: bool) -> YamlErrorOr[MapYamlNode]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if isinstance(n := node, MapYamlNode):
                return n

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value
                self.anchor_node_map[anchor_name] = n.value
                return self.get_map_node(check.not_none(n.value), is_merge)

            elif isinstance(n, AliasYamlNode):
                alias_name = check.not_none(check.not_none(n.value).get_token()).value
                node2 = self.anchor_node_map[alias_name]
                if node2 is None:
                    return yaml_error(f'cannot find anchor by alias name {alias_name}')
                return self.get_map_node(node2, is_merge)

            elif isinstance(n, SequenceYamlNode):
                if not is_merge:
                    return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.MAPPING, check.not_none(node.get_token()))  # noqa
                map_nodes: ta.List[MapYamlNode] = []
                for value in n.values:
                    map_node = self.get_map_node(check.not_none(value), False)
                    if isinstance(map_node, YamlError):
                        return map_node
                    map_nodes.append(map_node)
                return yaml_sequence_merge_value(*map_nodes)

            return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.MAPPING, check.not_none(node.get_token()))

        finally:
            self.step_out()

    def get_array_node(self, node: YamlNode) -> YamlErrorOr[ta.Optional[ArrayYamlNode]]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if isinstance(node, NullYamlNode):
                return None

            if isinstance(anchor := node, AnchorYamlNode):
                if isinstance(array_node := anchor.value, ArrayYamlNode):
                    return array_node

                return UnexpectedNodeTypeYamlError(check.not_none(anchor.value).type(), YamlNodeType.SEQUENCE, check.not_none(node.get_token()))  # noqa

            if isinstance(alias := node, AliasYamlNode):
                alias_name = check.not_none(check.not_none(alias.value).get_token()).value
                node2 = self.anchor_node_map[alias_name]
                if node2 is None:
                    return yaml_error(f'cannot find anchor by alias name {alias_name}')
                if isinstance(array_node := node2, ArrayYamlNode):
                    return array_node
                return UnexpectedNodeTypeYamlError(node2.type(), YamlNodeType.SEQUENCE, check.not_none(node2.get_token()))  # noqa

            if not isinstance(array_node := node, ArrayYamlNode):
                return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.SEQUENCE, check.not_none(node.get_token()))  # noqa

            return array_node

        finally:
            self.step_out()

    def decode_value(self, ctx: YamlDecodeContext, src: YamlNode) -> YamlErrorOr[ta.Any]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if src.type() == YamlNodeType.ANCHOR:
                anchor = check.isinstance(src, AnchorYamlNode)
                anchor_name = check.not_none(check.not_none(anchor.name).get_token()).value
                if isinstance(av := self.decode_value(ctx.with_anchor(anchor_name), check.not_none(anchor.value)), YamlError):  # noqa
                    return av
                self.anchor_value_map[anchor_name] = av
                return None

            src_val = self.node_to_value(ctx, src)
            if isinstance(src_val, YamlError):
                return src_val

            return src_val

        finally:
            self.step_out()

    def key_to_node_map(
        self,
        ctx: YamlDecodeContext,
        node: YamlNode,
        ignore_merge_key: bool,
        get_key_or_value_node: ta.Callable[[MapYamlNodeIter], YamlNode],
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            map_node = self.get_map_node(node, False)
            if isinstance(map_node, YamlError):
                return map_node
            key_map: ta.Dict[str, None] = {}
            key_to_node_map: ta.Dict[str, YamlNode] = {}
            map_iter = map_node.map_range()
            while map_iter.next():
                key_node = map_iter.key()
                if key_node.is_merge_key():
                    if ignore_merge_key:
                        continue
                    merge_map = self.key_to_node_map(ctx, map_iter.value(), ignore_merge_key, get_key_or_value_node)
                    if isinstance(merge_map, YamlError):
                        return merge_map
                    for k, v in merge_map.items():
                        if (err := self.validate_duplicate_key(key_map, k, v)) is not None:
                            return err
                        key_to_node_map[k] = v
                else:
                    key_val = self.node_to_value(ctx, key_node)
                    if isinstance(key_val, YamlError):
                        return key_val
                    if not isinstance(key := key_val, str):
                        return yaml_error('???')
                    if (err := self.validate_duplicate_key(key_map, key, key_node)) is not None:
                        return err
                    key_to_node_map[key] = get_key_or_value_node(map_iter)
            return key_to_node_map

        finally:
            self.step_out()

    def key_to_key_node_map(
        self,
        ctx: YamlDecodeContext,
        node: YamlNode,
        ignore_merge_key: bool,
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        m = self.key_to_node_map(ctx, node, ignore_merge_key, lambda node_map: node_map.key())
        if isinstance(m, YamlError):
            return m
        return m

    def key_to_value_node_map(
        self,
        ctx: YamlDecodeContext,
        node: YamlNode,
        ignore_merge_key: bool,
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        m = self.key_to_node_map(ctx, node, ignore_merge_key, lambda node_map: node_map.value())
        if isinstance(m, YamlError):
            return m
        return m

    # getParentMapTokenIfExists if the NodeType is a container type such as MappingType or SequenceType,
    # it is necessary to return the parent MapNode's colon token to represent the entire container.
    def get_parent_map_token_if_exists_for_validation_error(self, typ: YamlNodeType, tk: ta.Optional[YamlToken]) -> ta.Optional[YamlToken]:  # noqa
        if tk is None:
            return None
        if typ == YamlNodeType.MAPPING:
            # map:
            #   key: value
            #      ^ current token ( colon )
            if tk.prev is None:
                return tk
            key = tk.prev
            if key.prev is None:
                return tk
            return key.prev
        if typ == YamlNodeType.SEQUENCE:
            # map:
            #   - value
            #   ^ current token ( sequence entry )
            if tk.prev is None:
                return tk
            return tk.prev
        return tk

    def validate_duplicate_key(self, key_map: ta.Dict[str, None], key: ta.Any, key_node: YamlNode) -> ta.Optional[YamlError]:  # noqa
        if not isinstance(k := key, str):
            return None
        if not self.allow_duplicate_map_key:
            if k in key_map:
                return DuplicateKeyYamlError(f'duplicate key "{k}"', check.not_none(key_node.get_token()))
        key_map[k] = None
        return None

    def file_to_reader(self, file: str) -> YamlErrorOr[YamlBytesReader]:
        with open(file, 'rb') as f:
            bs = f.read()
        return ImmediateYamlBytesReader(bs)

    def is_yaml_file(self, file: str) -> bool:
        ext = file.rsplit('.', maxsplit=1)[-1]
        if ext == '.yml':
            return True
        if ext == '.yaml':
            return True
        return False

    def readers_under_dir(self, d: str) -> YamlErrorOr[ta.List[YamlBytesReader]]:
        pattern = f'{d}/*'
        matches = glob.glob(pattern)
        readers: ta.List[YamlBytesReader] = []
        for match in matches:
            if not self.is_yaml_file(match):
                continue
            if isinstance(reader := self.file_to_reader(match), YamlError):
                return reader
            readers.append(reader)
        return readers

    def readers_under_dir_recursive(self, d: str) -> YamlErrorOr[ta.List[YamlBytesReader]]:
        readers: ta.List[YamlBytesReader] = []
        for dp, _, fns in os.walk(d):
            for fn in fns:
                path = os.path.join(dp, fn)
                if not os.path.isfile(path):
                    continue
                if not self.is_yaml_file(path):
                    continue
                if isinstance(reader := self.file_to_reader(path), YamlError):
                    return reader
                readers.append(reader)
        return readers

    def resolve_reference(self, ctx: YamlDecodeContext) -> ta.Optional[YamlError]:
        for opt in self.opts:
            if (err := opt(self)) is not None:
                return err
        for file in self.reference_files:
            if isinstance(reader := self.file_to_reader(file), YamlError):
                return reader
            self.reference_readers.append(reader)
        for d in self.reference_dirs:
            if not self.is_recursive_dir:
                if isinstance(readers := self.readers_under_dir(d), YamlError):
                    return readers
                self.reference_readers.extend(readers)
            else:
                if isinstance(readers := self.readers_under_dir_recursive(d), YamlError):
                    return readers
                self.reference_readers.extend(readers)
        for reader in self.reference_readers:
            bs = reader.read()
            # assign new anchor definition to anchorMap
            if isinstance(err2 := self.parse(ctx, bs), YamlError):
                return err2
        self.is_resolved_reference = True
        return None

    def parse(self, ctx: YamlDecodeContext, bs: bytes) -> YamlErrorOr[YamlFile]:
        parse_mode: YamlParseMode = 0
        if self.to_comment_map is not None:
            parse_mode |= YAML_PARSE_COMMENTS
        opts: ta.List[YamlOption] = []
        if self.allow_duplicate_map_key:
            opts.append(yaml_allow_duplicate_map_key())
        if isinstance(f := yaml_parse_str(bs.decode(), parse_mode, *opts), YamlError):
            return f
        normalized_file = YamlFile()
        for doc in f.docs:
            # try to decode YamlNode to value and map anchor value to anchorMap
            if isinstance(v := self.node_to_value(ctx, check.not_none(doc.body)), YamlError):
                return v
            if v is not None or (doc.body is not None and doc.body.type() == YamlNodeType.NULL):
                normalized_file.docs.append(doc)
                cm = YamlCommentMap()
                cm.update(self.to_comment_map or {})
                self.comment_maps.append(cm)
            if self.to_comment_map is not None:
                self.to_comment_map.clear()
        return normalized_file

    def is_initialized(self) -> bool:
        return self.parsed_file is not None

    def decode_init(self, ctx: YamlDecodeContext) -> ta.Optional[YamlError]:
        if not self.is_resolved_reference:
            if (err := self.resolve_reference(ctx)) is not None:
                return err
        buf = self.reader.read()
        if isinstance(file := self.parse(ctx, buf), YamlError):
            return file
        self.parsed_file = file
        return None

    def _decode(self, ctx: YamlDecodeContext) -> YamlErrorOr[ta.Any]:
        self.decode_depth = 0
        self.anchor_value_map = {}
        pf = check.not_none(self.parsed_file)
        if len(pf.docs) == 0:
            # empty document.
            return None
        if len(pf.docs) <= self.stream_index:
            return EofYamlError()
        body = pf.docs[self.stream_index].body
        if body is None:
            return None
        if len(self.comment_maps) > self.stream_index:
            if (scm := self.comment_maps[self.stream_index]):
                check.not_none(self.to_comment_map).update(scm)
        if isinstance(v := self.decode_value(ctx, body), YamlError):
            return v
        self.stream_index += 1
        return v

    # Decode reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v.
    #
    # See the documentation for Unmarshal for details about the
    # conversion of YAML into a Go value.
    def decode(self) -> YamlErrorOr[ta.Any]:
        return self.decode_context(YamlDecodeContext())

    # decode_context reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v with Context.
    def decode_context(self, ctx: YamlDecodeContext) -> YamlErrorOr[ta.Any]:
        if self.is_initialized():
            if isinstance(v := self._decode(ctx), YamlError):
                return v
            return v
        if (err := self.decode_init(ctx)) is not None:
            return err
        if isinstance(v := self._decode(ctx), YamlError):
            return v
        return v

    # decode_from_node decodes node into the value pointed to by v.
    def decode_from_node(self, node: YamlNode) -> YamlErrorOr[ta.Any]:
        return self.decode_from_node_context(YamlDecodeContext(), node)

    # decode_from_node_context decodes node into the value pointed to by v with Context.
    def decode_from_node_context(self, ctx: YamlDecodeContext, node: YamlNode) -> YamlErrorOr[ta.Any]:
        if not self.is_initialized():
            if (err := self.decode_init(ctx)) is not None:
                return err
        # resolve references to the anchor on the same file
        if (err := self.node_to_value(ctx, node)) is not None:
            return err
        if isinstance(v := self.decode_value(ctx, node), YamlError):
            return v
        return v


##


def yaml_decode(s: str) -> ta.Any:
    d = YamlDecoder(ImmediateYamlBytesReader(s.encode()))
    if isinstance(v := d.decode(), YamlError):
        raise v
    return v


########################################
# _amalg.py


##
