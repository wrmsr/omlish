#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output tlog.py
# @omlish-git-diff-omit
# ruff: noqa: UP006 UP007 UP036 UP045 UP046
import abc
import collections
import dataclasses as dc
import functools
import io
import itertools
import logging
import os
import sys
import threading
import time
import traceback
import types
import typing as ta


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../omlish/lite/reflect.py
T = ta.TypeVar('T')

# ../../omlish/logs/levels.py
LogLevel = int  # ta.TypeAlias

# ../../omlish/logs/typed/types.py
U = ta.TypeVar('U')
TypedLoggerValueT = ta.TypeVar('TypedLoggerValueT', bound='TypedLoggerValue')
TypedLoggerValueOrProvider = ta.Union['TypedLoggerValue', 'TypedLoggerValueProvider']  # ta.TypeAlias
AbsentTypedLoggerValue = ta.Type['ABSENT_TYPED_LOGGER_VALUE']  # ta.TypeAlias
TypedLoggerValueOrAbsent = ta.Union['TypedLoggerValue', AbsentTypedLoggerValue]
TypedLoggerValueOrProviderOrAbsent = ta.Union[TypedLoggerValueOrProvider, AbsentTypedLoggerValue]  # ta.TypeAlias
TypedLoggerFieldValue = ta.Union[TypedLoggerValueOrProviderOrAbsent, ta.Type['TypedLoggerValue'], 'TypedLoggerConstFieldValue']  # ta.TypeAlias  # noqa
ResolvedTypedLoggerFieldValue = ta.Union[TypedLoggerValueOrAbsent, 'TypedLoggerConstFieldValue']  # ta.TypeAlias
UnwrappedTypedLoggerFieldValue = ta.Union[TypedLoggerValueOrAbsent, ta.Any]  # ta.TypeAlias

# ../../omlish/logs/typed/bindings.py
TypedLoggerBindingItem = ta.Union['TypedLoggerField', 'TypedLoggerValueOrProvider', 'TypedLoggerBindings', 'TypedLoggerValueWrapper']  # ta.TypeAlias  # noqa
TypedLoggerValueWrapperFn = ta.Callable[[ta.Any], 'TypedLoggerValue']  # ta.TypeAlias


########################################
# ../../../omlish/lite/abstract.py


##


_ABSTRACT_METHODS_ATTR = '__abstractmethods__'
_IS_ABSTRACT_METHOD_ATTR = '__isabstractmethod__'


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, _IS_ABSTRACT_METHOD_ATTR, False))


def update_abstracts(cls, *, force=False):
    if not force and not hasattr(cls, _ABSTRACT_METHODS_ATTR):
        # Per stdlib: We check for __abstractmethods__ here because cls might by a C implementation or a python
        # implementation (especially during testing), and we want to handle both cases.
        return cls

    abstracts: ta.Set[str] = set()

    for scls in cls.__bases__:
        for name in getattr(scls, _ABSTRACT_METHODS_ATTR, ()):
            value = getattr(cls, name, None)
            if getattr(value, _IS_ABSTRACT_METHOD_ATTR, False):
                abstracts.add(name)

    for name, value in cls.__dict__.items():
        if getattr(value, _IS_ABSTRACT_METHOD_ATTR, False):
            abstracts.add(name)

    setattr(cls, _ABSTRACT_METHODS_ATTR, frozenset(abstracts))
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
            ams = {a: cls for a, o in cls.__dict__.items() if is_abstract_method(o)}

            seen = set(cls.__dict__)
            for b in cls.__bases__:
                ams.update({a: b for a in set(getattr(b, _ABSTRACT_METHODS_ATTR, [])) - seen})  # noqa
                seen.update(dir(b))

            if ams:
                raise AbstractTypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: ' +
                    ', '.join(sorted([
                        '.'.join([
                            *([m] if (m := getattr(c, '__module__')) else []),
                            getattr(c, '__qualname__', getattr(c, '__name__')),
                            a,
                        ])
                        for a, c in ams.items()
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
# ../../../omlish/lite/reflect.py


##


_GENERIC_ALIAS_TYPES = (
    ta._GenericAlias,  # type: ignore  # noqa
    *([ta._SpecialGenericAlias] if hasattr(ta, '_SpecialGenericAlias') else []),  # noqa
)


def is_generic_alias(obj: ta.Any, *, origin: ta.Any = None) -> bool:
    return (
        isinstance(obj, _GENERIC_ALIAS_TYPES) and
        (origin is None or ta.get_origin(obj) is origin)
    )


is_callable_alias = functools.partial(is_generic_alias, origin=ta.Callable)


##


_UNION_ALIAS_ORIGINS = frozenset([
    ta.get_origin(ta.Optional[int]),
    *(
        [
            ta.get_origin(int | None),
            ta.get_origin(getattr(ta, 'TypeVar')('_T') | None),
        ] if sys.version_info >= (3, 10) else ()
    ),
])


def is_union_alias(obj: ta.Any) -> bool:
    return ta.get_origin(obj) in _UNION_ALIAS_ORIGINS


#


def is_optional_alias(spec: ta.Any) -> bool:
    return (
        is_union_alias(spec) and
        len(ta.get_args(spec)) == 2 and
        any(a in (None, type(None)) for a in ta.get_args(spec))
    )


def get_optional_alias_arg(spec: ta.Any) -> ta.Any:
    [it] = [it for it in ta.get_args(spec) if it not in (None, type(None))]
    return it


##


def is_new_type(spec: ta.Any) -> bool:
    if isinstance(ta.NewType, type):
        return isinstance(spec, ta.NewType)
    else:
        # Before https://github.com/python/cpython/commit/c2f33dfc83ab270412bf243fb21f724037effa1a
        return isinstance(spec, types.FunctionType) and spec.__code__ is ta.NewType.__code__.co_consts[1]  # type: ignore  # noqa


def get_new_type_supertype(spec: ta.Any) -> ta.Any:
    return spec.__supertype__


##


def is_literal_type(spec: ta.Any) -> bool:
    if hasattr(ta, '_LiteralGenericAlias'):
        return isinstance(spec, ta._LiteralGenericAlias)  # noqa
    else:
        return (
            isinstance(spec, ta._GenericAlias) and  # type: ignore  # noqa
            spec.__origin__ is ta.Literal
        )


def get_literal_type_args(spec: ta.Any) -> ta.Iterable[ta.Any]:
    return spec.__args__


########################################
# ../../../omlish/lite/strings.py


##


def camel_case(name: str, *, lower: bool = False) -> str:
    if not name:
        return ''
    s = ''.join(map(str.capitalize, name.split('_')))  # noqa
    if lower:
        s = s[0].lower() + s[1:]
    return s


def snake_case(name: str) -> str:
    uppers: list[int | None] = [i for i, c in enumerate(name) if c.isupper()]
    return '_'.join([name[l:r].lower() for l, r in zip([None, *uppers], [*uppers, None])]).strip('_')


##


def is_dunder(name: str) -> bool:
    return (
        name[:2] == name[-2:] == '__' and
        name[2:3] != '_' and
        name[-3:-2] != '_' and
        len(name) > 4
    )


def is_sunder(name: str) -> bool:
    return (
        name[0] == name[-1] == '_' and
        name[1:2] != '_' and
        name[-2:-1] != '_' and
        len(name) > 2
    )


##


def strip_with_newline(s: str) -> str:
    if not s:
        return ''
    return s.strip() + '\n'


@ta.overload
def split_keep_delimiter(s: str, d: str) -> str:
    ...


@ta.overload
def split_keep_delimiter(s: bytes, d: bytes) -> bytes:
    ...


def split_keep_delimiter(s, d):
    ps = []
    i = 0
    while i < len(s):
        if (n := s.find(d, i)) < i:
            ps.append(s[i:])
            break
        ps.append(s[i:n + 1])
        i = n + 1
    return ps


##


def attr_repr(obj: ta.Any, *attrs: str) -> str:
    return f'{type(obj).__name__}({", ".join(f"{attr}={getattr(obj, attr)!r}" for attr in attrs)})'


##


FORMAT_NUM_BYTES_SUFFIXES: ta.Sequence[str] = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']


def format_num_bytes(num_bytes: int) -> str:
    for i, suffix in enumerate(FORMAT_NUM_BYTES_SUFFIXES):
        value = num_bytes / 1024 ** i
        if num_bytes < 1024 ** (i + 1):
            if value.is_integer():
                return f'{int(value)}{suffix}'
            else:
                return f'{value:.2f}{suffix}'

    return f'{num_bytes / 1024 ** (len(FORMAT_NUM_BYTES_SUFFIXES) - 1):.2f}{FORMAT_NUM_BYTES_SUFFIXES[-1]}'


########################################
# ../../../omlish/lite/wrappers.py


##


_ANNOTATION_ATTRS: ta.FrozenSet[str] = frozenset([
    '__annotations__',

    '__annotate__',
    '__annotate_func__',

    '__annotations_cache__',
])

_UPDATE_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS: ta.Sequence[str] = list(frozenset(functools.WRAPPER_ASSIGNMENTS) - _ANNOTATION_ATTRS)  # noqa


def update_wrapper_no_annotations(wrapper, wrapped):
    functools.update_wrapper(wrapper, wrapped, assigned=_UPDATE_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS)
    return wrapper


########################################
# ../../../omlish/logs/callers.py


##


class LoggingCaller(ta.NamedTuple):
    filename: str
    lineno: int
    func: str
    sinfo: ta.Optional[str]

    @classmethod
    def find_frame(cls, ofs: int = 0) -> types.FrameType:
        f: ta.Any = sys._getframe(2 + ofs)  # noqa
        while hasattr(f, 'f_code'):
            if f.f_code.co_filename != __file__:
                return f
            f = f.f_back
        raise RuntimeError

    @classmethod
    def find(cls, stack_info: bool = False) -> 'LoggingCaller':
        f = cls.find_frame(1)
        # TODO: ('(unknown file)', 0, '(unknown function)', None) ?

        sinfo = None
        if stack_info:
            sio = io.StringIO()
            sio.write('Stack (most recent call last):\n')
            traceback.print_stack(f, file=sio)
            sinfo = sio.getvalue()
            sio.close()
            if sinfo[-1] == '\n':
                sinfo = sinfo[:-1]

        return cls(
            f.f_code.co_filename,
            f.f_lineno,
            f.f_code.co_name,
            sinfo,
        )


########################################
# ../../../omlish/logs/levels.py


##


########################################
# ../../../omlish/logs/typed/types.py


##


class _TypedLoggerInternalMethods(ta.Protocol):  # noqa
    def _typed_logger_provide_value(self, ctx: 'TypedLoggerContext') -> TypedLoggerValueOrAbsent: ...  # noqa

    def _typed_logger_maybe_provide_default_value(self, ctx: 'TypedLoggerContext') -> ta.Tuple[TypedLoggerValueOrAbsent, ...]: ... # noqa

    def _typed_logger_resolve_field_value(self, ctx: 'TypedLoggerContext') -> ResolvedTypedLoggerFieldValue: ...  # noqa

    def _typed_logger_unwrap_field_value(self, ctx: 'TypedLoggerContext') -> UnwrappedTypedLoggerFieldValue: ...  # noqa

    def _typed_logger_visit_bindings(self, vst: 'TypedLoggerBindings._Visitor') -> None:  ...  # noqa


##


@ta.final
class ABSENT_TYPED_LOGGER_VALUE:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    @classmethod
    def map_absent(cls, fn: ta.Callable[[TypedLoggerValueT], U]) -> AbsentTypedLoggerValue:  # noqa
        return cls

    #

    @classmethod
    def _typed_logger_provide_value(cls, ctx: 'TypedLoggerContext') -> TypedLoggerValueOrAbsent:  # noqa
        return cls

    @classmethod
    def _typed_logger_resolve_field_value(cls, ctx: 'TypedLoggerContext') -> ResolvedTypedLoggerFieldValue:  # noqa
        return cls

    @classmethod
    def _typed_logger_unwrap_field_value(cls, ctx: 'TypedLoggerContext') -> UnwrappedTypedLoggerFieldValue:  # noqa
        return cls


##


class TypedLoggerValue(Abstract, ta.Generic[T]):
    def __init__(self, v: T) -> None:
        self._v = v

    @classmethod
    def of(cls: ta.Type[TypedLoggerValueT], v: ta.Any) -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        return cls(v) if v is not ABSENT_TYPED_LOGGER_VALUE else ABSENT_TYPED_LOGGER_VALUE

    @property
    def v(self) -> T:
        return self._v

    def __repr__(self) -> str:
        return f'{self.__class__.__module__}.{self.__class__.__qualname__}({self._v!r})'

    #

    def map_absent(  # noqa
            self: TypedLoggerValueT,
            fn: ta.Callable[[TypedLoggerValueT], U],
    ) -> ta.Union[U, AbsentTypedLoggerValue]:
        return fn(self)

    #

    _hash: int

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass
        h = self._hash = hash((self.__class__, self.v))
        return h

    def __eq__(self, o):
        if not isinstance(o, TypedLoggerValue):
            return NotImplemented
        return self.__class__ is o.__class__ and self.v == o.v

    def __ne__(self, o):
        return not (self == o)

    #

    _default_key: ta.ClassVar[ta.Union[str, bool]] = False

    @ta.final
    @classmethod
    def default_key(cls) -> ta.Optional[str]:
        return cls.__default_key  # type: ignore[attr-defined]

    #

    class ContextLambda(ta.NamedTuple):
        fn: ta.Callable[['TypedLoggerContext'], ta.Any]

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if '__call__' in cls.__dict__:
            raise TypeError(f'{cls} should not be callable')

        try:
            dtb = DefaultTypedLoggerValue
        except NameError:
            pass
        else:
            if hasattr(cls, '_default_value') and not issubclass(cls, dtb):
                raise TypeError(f'{cls} should be a subclass of DefaultTypedLoggerValue if it has a _default_value')

        dks: ta.Optional[str]
        if isinstance((dk := getattr(cls, '_default_key')), str):
            dks = dk
        elif dk is True:
            dks = snake_case(cls.__name__)
        elif dk is False:
            dks = None
        else:
            raise TypeError(dk)
        cls.__default_key = dks  # type: ignore[attr-defined]

    #

    @ta.final
    def _typed_logger_provide_value(self, ctx: 'TypedLoggerContext') -> TypedLoggerValueOrAbsent:  # noqa
        return self

    @classmethod
    def _typed_logger_maybe_provide_default_value(cls, ctx: 'TypedLoggerContext') -> ta.Tuple[TypedLoggerValueOrAbsent, ...]:  # noqa
        return ()

    @ta.final
    def _typed_logger_resolve_field_value(self, ctx: 'TypedLoggerContext') -> ResolvedTypedLoggerFieldValue:  # noqa
        return self

    @ta.final
    def _typed_logger_unwrap_field_value(self, ctx: 'TypedLoggerContext') -> UnwrappedTypedLoggerFieldValue:  # noqa
        return self._v

    @ta.final
    def _typed_logger_visit_bindings(self, vst: 'TypedLoggerBindings._Visitor') -> None:  # noqa
        vst.accept_values(((type(self), self),))
        vst.accept_const_values(((type(self), self),))


class DefaultTypedLoggerValue(TypedLoggerValue[T], Abstract):
    _default_value: ta.ClassVar[ta.Union[
        AbsentTypedLoggerValue,
        classmethod,
        TypedLoggerValue.ContextLambda,
        ta.Any,
    ]] = ABSENT_TYPED_LOGGER_VALUE

    @ta.final
    @classmethod
    def default_provider(cls) -> 'TypedLoggerValueProvider':
        try:
            return cls.__default_provider  # type: ignore[attr-defined]
        except AttributeError:
            pass

        # Must be done late to support typing forwardrefs.
        dp: TypedLoggerValueProvider
        dv = next(mc.__dict__['_default_value'] for mc in cls.__mro__ if '_default_value' in mc.__dict__)

        if dv is ABSENT_TYPED_LOGGER_VALUE:
            dp = ConstTypedLoggerValueProvider(cls, ABSENT_TYPED_LOGGER_VALUE)

        elif isinstance(dv, classmethod):
            fn = dv.__get__(None, cls)
            fl: ta.Any = lambda **kw: cls(v) if (v := fn(**kw)) is not ABSENT_TYPED_LOGGER_VALUE else v
            dp = FnTypedLoggerValueProvider(cls, update_wrapper_no_annotations(fl, fn))

        elif isinstance(dv, TypedLoggerValue.ContextLambda):
            fl = lambda ctx: cls(dv.fn(ctx))
            dp = ContextFnTypedLoggerValueProvider(cls, update_wrapper_no_annotations(fl, dv.fn))

        else:
            dp = ConstTypedLoggerValueProvider(cls, cls(dv))

        cls.__default_provider = dp  # type: ignore[attr-defined]
        return dp

    #

    @ta.final
    @classmethod
    def _typed_logger_maybe_provide_default_value(cls, ctx: 'TypedLoggerContext') -> ta.Tuple[TypedLoggerValueOrAbsent, ...]:  # noqa
        return (cls.default_provider().provide_value(ctx),)


##


class TypedLoggerValueProvider(Abstract, ta.Generic[TypedLoggerValueT]):
    @property
    @abc.abstractmethod
    def cls(self) -> ta.Type[TypedLoggerValueT]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_value(self, ctx: 'TypedLoggerContext') -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        raise NotImplementedError

    #

    @ta.final
    def _typed_logger_provide_value(self, ctx: 'TypedLoggerContext') -> TypedLoggerValueOrAbsent:  # noqa
        return self.provide_value(ctx)

    @ta.final
    def _typed_logger_resolve_field_value(self, ctx: 'TypedLoggerContext') -> ResolvedTypedLoggerFieldValue:  # noqa
        return self.provide_value(ctx)

    def _typed_logger_visit_bindings(self, vst: 'TypedLoggerBindings._Visitor') -> None:  # noqa
        vst.accept_values(((self.cls, self),))


#


class ConstTypedLoggerValueProvider(TypedLoggerValueProvider[TypedLoggerValueT]):
    def __init__(
            self,
            cls: ta.Type[TypedLoggerValueT],
            v: ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue],
    ) -> None:
        super().__init__()

        self._cls = cls
        self._v = v

    @property
    def cls(self) -> ta.Type[TypedLoggerValueT]:
        return self._cls

    @property
    def v(self) -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        return self._v

    def provide_value(self, ctx: 'TypedLoggerContext') -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        return self._v

    #

    @ta.final
    def _typed_logger_visit_bindings(self, vst: 'TypedLoggerBindings._Visitor') -> None:  # noqa
        vst.accept_values(((self.cls, self),))
        vst.accept_const_values(((self.cls, self._v),))


#


@ta.final
class ContextFnTypedLoggerValueProvider(TypedLoggerValueProvider[TypedLoggerValueT]):
    def __init__(
            self,
            cls: ta.Type[TypedLoggerValueT],
            fn: ta.Callable[['TypedLoggerContext'], ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]],
    ) -> None:
        super().__init__()

        self._cls = cls
        self._fn = fn

    @property
    def cls(self) -> ta.Type[TypedLoggerValueT]:
        return self._cls

    @property
    def fn(self) -> ta.Callable[['TypedLoggerContext'], ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]]:
        return self._fn

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._cls!r}, {self._fn!r})'

    def provide_value(self, ctx: 'TypedLoggerContext') -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        return self._fn(ctx)


#


class FnTypedLoggerValueProviderAnnotationError(TypeError):
    pass


@ta.final
class FnTypedLoggerValueProvider(TypedLoggerValueProvider[TypedLoggerValueT]):
    def __init__(
            self,
            cls: ta.Type[TypedLoggerValueT],
            fn: ta.Callable[[], ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]],
    ) -> None:
        super().__init__()

        self._cls = cls
        self._fn = fn

        self._kw = self._get_fn_kwargs(fn)

    @classmethod
    def _get_fn_kwargs(cls, fn: ta.Any) -> ta.Mapping[str, ta.Type[TypedLoggerValue]]:
        o = fn
        s = {o}
        while hasattr(o, '__wrapped__'):
            o = o.__wrapped__
            if o in s:
                raise RuntimeError(f'Recursive unwrap: {o!r} in {s!r}')
            s.add(o)

        def get_kw(anns: ta.Dict[str, ta.Any]) -> ta.Dict[str, ta.Type[TypedLoggerValue]]:
            anns = dict(anns)
            anns.pop('return', None)
            if not anns:
                return {}

            kw: ta.Dict[str, ta.Type[TypedLoggerValue]] = {}
            for k, v in anns.items():
                def bad() -> ta.NoReturn:
                    raise FnTypedLoggerValueProviderAnnotationError(
                        f'{fn} has invalid annotation {k} of {v} - must be subtype of TypedLoggerValue or'  # noqa
                        f'Union[TypedLoggerValue, AbsentTypedLoggerValue]',
                    )

                a = v
                if is_union_alias(a):
                    if len(us := set(a)) != 2 or AbsentTypedLoggerValue not in us:
                        bad()
                    [a] = us - {AbsentTypedLoggerValue}

                if not (isinstance(a, type) and issubclass(a, TypedLoggerValue)):
                    bad()

                kw[k] = a

            return kw

        try:
            # Note: transparently falls back to magic property on 3.14+
            return get_kw(getattr(o, '__annotations__', {}))
        except FnTypedLoggerValueProviderAnnotationError:
            pass

        # This is much slower, so only do it if necessary.
        return get_kw(ta.get_type_hints(o))

    @property
    def cls(self) -> ta.Type[TypedLoggerValueT]:
        return self._cls

    @property
    def fn(self) -> ta.Callable[[], ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]]:
        return self._fn

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._cls!r}, {self._fn!r})'

    def provide_value(self, ctx: 'TypedLoggerContext') -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        return self._fn(**{
            k: v
            for k, c in self._kw.items()
            if (v := ctx[c]) is not ABSENT_TYPED_LOGGER_VALUE
        })


##


@ta.final
class TypedLoggerConstFieldValue(ta.NamedTuple):
    v: ta.Any

    #

    @ta.final
    def _typed_logger_resolve_field_value(self, ctx: 'TypedLoggerContext') -> ResolvedTypedLoggerFieldValue:  # noqa
        return self

    @ta.final
    def _typed_logger_unwrap_field_value(self, ctx: 'TypedLoggerContext') -> UnwrappedTypedLoggerFieldValue:  # noqa
        return self.v


@ta.final
class TypedLoggerField(ta.NamedTuple):
    k: str
    v: TypedLoggerFieldValue

    #

    def _typed_logger_visit_bindings(self, vst: 'TypedLoggerBindings._Visitor') -> None:  # noqa
        vst.accept_keys(((self.k, self.v),))


##


TYPED_LOGGER_VALUE_OR_PROVIDER_TYPES: ta.Tuple[ta.Type[TypedLoggerValueOrProvider], ...] = (
    TypedLoggerValue,
    TypedLoggerValueProvider,
)

TYPED_LOGGER_VALUE_OR_ABSENT_TYPES: ta.Tuple[ta.Union[
    ta.Type[TypedLoggerValue],
    AbsentTypedLoggerValue,
], ...] = (
    TypedLoggerValue,
    ABSENT_TYPED_LOGGER_VALUE,
)

TYPED_LOGGER_VALUE_OR_PROVIDER_OR_ABSENT_TYPES: ta.Tuple[ta.Union[
    ta.Type[TypedLoggerValueOrProvider],
    AbsentTypedLoggerValue,
], ...] = (
    *TYPED_LOGGER_VALUE_OR_PROVIDER_TYPES,
    ABSENT_TYPED_LOGGER_VALUE,
)


##


@ta.overload
def unwrap_typed_logger_field_value(rfv: TypedLoggerValue[T]) -> TypedLoggerValue[T]:
    ...


@ta.overload
def unwrap_typed_logger_field_value(rfv: AbsentTypedLoggerValue) -> AbsentTypedLoggerValue:
    ...


@ta.overload
def unwrap_typed_logger_field_value(rfv: TypedLoggerConstFieldValue) -> ta.Any:
    ...


def unwrap_typed_logger_field_value(rfv):
    return rfv._typed_logger_unwrap_field_value(rfv)  # noqa


########################################
# ../../../omlish/logs/typed/bindings.py
"""
TODO:
 - optimization of just using ChainMap when override?
  - TypedLoggerBindings as Abstract, FullTLB and LimitedTLB subtypes, limited
 - TypedLoggerBindingsBuilder ?
"""


##


class TypedLoggerDuplicateBindingsError(Exception):
    def __init__(
            self,
            *,
            keys: ta.Optional[ta.Dict[str, ta.List[TypedLoggerFieldValue]]] = None,
            values: ta.Optional[ta.Dict[ta.Type[TypedLoggerValue], ta.List[TypedLoggerValueOrProviderOrAbsent]]] = None,
            wrappers: ta.Optional[ta.Dict[type, ta.List[TypedLoggerValueWrapperFn]]] = None,
    ) -> None:
        super().__init__()

        self.keys = keys
        self.values = values
        self.wrappers = wrappers

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(' +
            ', '.join([
                *([f'keys={self.keys!r}'] if self.keys is not None else []),
                *([f'values={self.values!r}'] if self.values is not None else []),
                *([f'wrappers={self.wrappers!r}'] if self.wrappers is not None else []),
            ]) +
            f')'
        )


class TypedLoggerBindings(Abstract):
    @property
    @abc.abstractmethod
    def key_map(self) -> ta.Mapping[str, TypedLoggerFieldValue]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def const_value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def value_wrapper_fn(self) -> ta.Optional[TypedLoggerValueWrapperFn]:
        raise NotImplementedError

    #

    @ta.final
    class _Visitor(ta.NamedTuple):
        accept_key: ta.Callable[[str, TypedLoggerFieldValue], None]
        accept_keys: ta.Callable[[ta.Iterable[ta.Tuple[str, TypedLoggerFieldValue]]], None]

        accept_value: ta.Callable[[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent], None]
        accept_values: ta.Callable[[ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]]], None]  # noqa

        accept_const_values: ta.Callable[[ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]]], None]  # noqa

        accept_value_wrapping: ta.Callable[[ta.Union['TypedLoggerValueWrapper', 'FullTypedLoggerBindings._ValueWrappingState']], None]  # noqa

    @abc.abstractmethod
    def _typed_logger_visit_bindings(self, vst: _Visitor) -> None:
        raise NotImplementedError


##


@ta.final
class FullTypedLoggerBindings(TypedLoggerBindings):
    def __init__(
            self,
            *items: TypedLoggerBindingItem,
            override: bool = False,
    ) -> None:
        kd: ta.Dict[str, TypedLoggerFieldValue] = {}
        dup_kd: ta.Dict[str, ta.List[TypedLoggerFieldValue]] = {}

        vd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent] = {}
        dup_vd: ta.Dict[ta.Type[TypedLoggerValue], ta.List[TypedLoggerValueOrProviderOrAbsent]] = {}

        cvd: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = {}

        vst: TypedLoggerBindings._Visitor

        vwl: ta.List[ta.Union[TypedLoggerValueWrapper, FullTypedLoggerBindings._ValueWrappingState]] = []

        if not override:
            def add_kd(kd_k: str, kd_v: TypedLoggerFieldValue) -> None:  # noqa
                if kd_k in kd:
                    dup_kd.setdefault(kd_k, []).append(kd_v)
                else:
                    kd[kd_k] = kd_v

            def add_vd(vd_k: ta.Type[TypedLoggerValue], vd_v: TypedLoggerValueOrProviderOrAbsent) -> None:  # noqa
                if vd_k in vd:
                    dup_vd.setdefault(vd_k, []).append(vd_v)
                else:
                    vd[vd_k] = vd_v

            def add_kds(it: ta.Iterable[ta.Tuple[str, TypedLoggerFieldValue]]) -> None:  # noqa
                collections.deque(itertools.starmap(add_kd, it), maxlen=0)

            def add_vds(it: ta.Iterable[ta.Tuple[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]]) -> None:  # noqa
                collections.deque(itertools.starmap(add_vd, it), maxlen=0)

            vst = TypedLoggerBindings._Visitor(  # noqa
                add_kd,
                add_kds,

                add_vd,
                add_vds,

                cvd.update,

                vwl.append,
            )

        else:
            vst = TypedLoggerBindings._Visitor(  # noqa
                kd.__setitem__,
                kd.update,

                vd.__setitem__,
                vd.update,

                cvd.update,

                vwl.append,
            )

        for o in items:
            o._typed_logger_visit_bindings(vst)  # noqa

        #

        dup_vwd: ta.Optional[ta.Dict[type, ta.List[TypedLoggerValueWrapperFn]]] = None

        vws: ta.Optional[FullTypedLoggerBindings._ValueWrappingState] = None
        vwf: ta.Optional[TypedLoggerValueWrapperFn] = None

        if vwl:
            if len(vwl) == 1 and isinstance((vwl0 := vwl[0]), FullTypedLoggerBindings._ValueWrappingState):
                vws = vwl0

            else:
                vwd: ta.Dict[type, TypedLoggerValueWrapperFn] = {}

                add_vwd: ta.Callable[[type, TypedLoggerValueWrapperFn], None]

                if not override:
                    dup_vwd = {}

                    def add_vwd(vw_ty: type, vw_fn: TypedLoggerValueWrapperFn) -> None:  # noqa
                        if vw_ty in vwd:
                            dup_vwd.setdefault(vw_ty, []).append(vw_fn)
                        else:
                            vwd[vw_ty] = vw_fn

                else:
                    add_vwd = vwd.__setitem__

                for vo in vwl:
                    vo._typed_logger_visit_value_wrappers(add_vwd)  # noqa

                if vwd and not dup_vwd:
                    vws = FullTypedLoggerBindings._ValueWrappingState(vwd)
                    vwf = vws.sdf

        #

        if dup_kd or dup_vd or dup_vwd:
            raise TypedLoggerDuplicateBindingsError(
                keys=dup_kd or None,
                values=dup_vd or None,
                wrappers=dup_vwd or None,
            )

        self._key_map: ta.Mapping[str, TypedLoggerFieldValue] = kd
        self._value_map: ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent] = vd

        self._const_value_map: ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = cvd

        self._value_wrapping = vws
        self._value_wrapper_fn = vwf

    #

    @property
    def key_map(self) -> ta.Mapping[str, TypedLoggerFieldValue]:
        return self._key_map

    @property
    def value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrProviderOrAbsent]:
        return self._value_map

    @property
    def const_value_map(self) -> ta.Mapping[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent]:
        return self._const_value_map

    @property
    def value_wrapper_fn(self) -> ta.Optional[TypedLoggerValueWrapperFn]:
        return self._value_wrapper_fn

    #

    @ta.final
    class _ValueWrappingState:
        def __init__(self, dct: ta.Mapping[type, TypedLoggerValueWrapperFn]) -> None:
            self.dct = dct

            @functools.singledispatch
            def wrap_value(o: ta.Any) -> TypedLoggerValue:
                raise UnhandledTypedValueWrapperTypeError(o)

            collections.deque(itertools.starmap(wrap_value.register, self.dct.items()), maxlen=0)

            self.sdf = wrap_value

        #

        def _typed_logger_visit_value_wrappers(self, fn: ta.Callable[[type, TypedLoggerValueWrapperFn], None]) -> None:  # noqa
            collections.deque(itertools.starmap(fn, self.dct.items()), maxlen=0)

    #

    def _typed_logger_visit_bindings(self, vst: TypedLoggerBindings._Visitor) -> None:
        vst.accept_keys(self._key_map.items())
        vst.accept_values(self._value_map.items())

        vst.accept_const_values(self._const_value_map.items())

        if (vws := self._value_wrapping) is not None:
            vst.accept_value_wrapping(vws)


##


class UnhandledTypedValueWrapperTypeError(TypeError):
    pass


@ta.final
class TypedLoggerValueWrapper(ta.NamedTuple):
    tys: ta.AbstractSet[type]
    fn: TypedLoggerValueWrapperFn

    #

    def _typed_logger_visit_bindings(self, vst: TypedLoggerBindings._Visitor) -> None:  # noqa
        vst.accept_value_wrapping(self)

    def _typed_logger_visit_value_wrappers(self, fn: ta.Callable[[type, TypedLoggerValueWrapperFn], None]) -> None:  # noqa
        for ty in self.tys:
            fn(ty, self.fn)


##


TYPED_LOGGER_BINDING_ITEM_TYPES: ta.Tuple[ta.Type[TypedLoggerBindingItem], ...] = (
    TypedLoggerField,
    *TYPED_LOGGER_VALUE_OR_PROVIDER_TYPES,
    TypedLoggerBindings,
    TypedLoggerValueWrapper,
)


##


CanTypedLoggerBinding = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    TypedLoggerBindingItem,
    ta.Type[TypedLoggerValue],
    ta.Tuple[
        str,
        ta.Union[
            TypedLoggerFieldValue,
            ta.Any,
        ],
    ],
    None,
]


_AS_TYPED_LOGGER_BINDINGS_DIRECT_TYPES: ta.Tuple[type, ...] = (
    TypedLoggerField,
    TypedLoggerBindings,
    TypedLoggerValueWrapper,
)

_AS_TYPED_LOGGER_BINDINGS_FIELD_VALUE_DIRECT_TYPES: ta.Tuple[type, ...] = (
    *TYPED_LOGGER_VALUE_OR_PROVIDER_OR_ABSENT_TYPES,
    TypedLoggerConstFieldValue,
)


def as_typed_logger_bindings(
        *objs: CanTypedLoggerBinding,

        add_default_keys: bool = False,
        default_key_filter: ta.Optional[ta.Callable[[str], bool]] = None,

        add_default_values: bool = False,
        default_value_filter: ta.Optional[ta.Callable[[ta.Type[DefaultTypedLoggerValue]], bool]] = None,

        value_wrapper: ta.Optional[TypedLoggerValueWrapperFn] = None,
) -> ta.Sequence[TypedLoggerBindingItem]:
    """This functionality is combined to preserve final key ordering."""

    lst: ta.List[TypedLoggerBindingItem] = []

    for o in objs:
        if o is None:
            continue

        elif isinstance(o, _AS_TYPED_LOGGER_BINDINGS_DIRECT_TYPES):
            lst.append(o)  # type: ignore[arg-type]

        elif isinstance(o, TypedLoggerValue):
            lst.append(o)

            if add_default_keys:
                if (dk := o.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, o))

        elif isinstance(o, TypedLoggerValueProvider):
            lst.append(o)

            if add_default_keys:
                if (dk := o.cls.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, o))

        elif isinstance(o, type) and issubclass(o, TypedLoggerValue):
            b = False

            if add_default_values and issubclass(o, DefaultTypedLoggerValue):
                if (dp := o.default_provider()) is not None:
                    if default_value_filter is None or default_value_filter(o):
                        lst.append(dp)
                        b = True

            if add_default_keys:
                if (dk := o.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, o))
                        b = True

            if not b:
                raise TypeError(f'{o} was added as neither a default key nor a default value')

        elif isinstance(o, tuple):
            k, v = o
            if not isinstance(k, str):
                raise TypeError(k)

            if (
                    isinstance(v, _AS_TYPED_LOGGER_BINDINGS_FIELD_VALUE_DIRECT_TYPES) or
                    (isinstance(o, type) and issubclass(o, TypedLoggerValue))  # type: ignore[unreachable]
            ):
                lst.append(TypedLoggerField(k, v))  # type: ignore[arg-type]

            else:
                lst.append(TypedLoggerField(k, TypedLoggerConstFieldValue(v)))

        elif value_wrapper is not None:
            wv = value_wrapper(o)
            if not isinstance(wv, TypedLoggerValue):
                raise TypeError(wv)

            lst.append(wv)

            if add_default_keys:
                if (dk := wv.default_key()) is not None:
                    if default_key_filter is None or default_key_filter(dk):
                        lst.append(TypedLoggerField(dk, wv))

        else:
            # ta.assert_never(o)
            raise TypeError(o)

    return lst


########################################
# ../../../omlish/logs/typed/contexts.py


##


class RecursiveTypedLoggerValueError(Exception):
    def __init__(self, cls: ta.Type[TypedLoggerValue], rec: ta.Sequence[ta.Type[TypedLoggerValue]]) -> None:
        super().__init__()

        self.cls = cls
        self.rec = rec

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'cls={self.cls!r}, '
            f'rec={self.rec!r}'
            f')'
        )


class UnboundTypedLoggerValueError(Exception):
    def __init__(self, cls: ta.Type[TypedLoggerValue]) -> None:
        super().__init__()

        self.cls = cls

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(cls={self.cls!r})'


#


@ta.final
class TypedLoggerContext:
    def __init__(
            self,
            bindings: 'TypedLoggerBindings',
            *,
            no_auto_default_values: bool = False,
            default_absent: bool = False,
    ) -> None:
        super().__init__()

        self._bindings = bindings
        self._no_auto_default_values = no_auto_default_values
        self._default_absent = default_absent

        self._values: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = dict(bindings.const_value_map)  # noqa
        self._rec: ta.Dict[ta.Type[TypedLoggerValue], None] = {}

    @property
    def bindings(self) -> 'TypedLoggerBindings':
        return self._bindings

    @property
    def no_auto_default_values(self) -> bool:
        return self._no_auto_default_values

    @property
    def default_absent(self) -> bool:
        return self._default_absent

    #

    def __getitem__(self, cls: ta.Type[TypedLoggerValueT]) -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        try:
            return self._values[cls]  # type: ignore[return-value]
        except KeyError:
            pass

        if not issubclass(cls, TypedLoggerValue):
            raise TypeError(cls)

        if cls in self._rec:
            raise RecursiveTypedLoggerValueError(cls, list(self._rec))

        self._rec[cls] = None
        try:
            v: ta.Union[TypedLoggerValueOrAbsent]

            try:
                bv = self._bindings.value_map[cls]

            except KeyError:
                if not self._no_auto_default_values and (dt := cls._typed_logger_maybe_provide_default_value(self)):
                    [v] = dt

                elif self._default_absent:
                    v = ABSENT_TYPED_LOGGER_VALUE

                else:
                    raise UnboundTypedLoggerValueError(cls) from None

            else:
                if bv is ABSENT_TYPED_LOGGER_VALUE:  # noqa
                    v = ABSENT_TYPED_LOGGER_VALUE

                else:
                    v = bv._typed_logger_provide_value(self)  # noqa

            self._values[cls] = v
            return v  # type: ignore[return-value]

        finally:
            self._rec.pop(cls)

    #

    def resolve_field_value(self, fv: TypedLoggerFieldValue) -> ResolvedTypedLoggerFieldValue:
        if fv is ABSENT_TYPED_LOGGER_VALUE:
            return fv  # type: ignore[return-value]

        elif isinstance(fv, type):
            return self[fv]._typed_logger_resolve_field_value(self)  # type: ignore[type-var]  # noqa

        else:
            return fv._typed_logger_resolve_field_value(self)  # noqa

    def unwrap_field_value(self, fv: TypedLoggerFieldValue) -> UnwrappedTypedLoggerFieldValue:
        return unwrap_typed_logger_field_value(self.resolve_field_value(fv))


########################################
# ../../../omlish/logs/typed/values.py


##


class StandardTypedLoggerValues:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    class TimeNs(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> float:
            return time.time()

    class Time(DefaultTypedLoggerValue[float]):
        _default_key = True
        _default_value = TypedLoggerValue.ContextLambda(
            lambda ctx: ctx[StandardTypedLoggerValues.TimeNs].map_absent(
                lambda tv: tv.v / 1e9,
            ),
        )

    #

    class Level(TypedLoggerValue[LogLevel]):
        pass

    class LevelName(DefaultTypedLoggerValue[str]):
        _default_key = 'level'
        _default_value = TypedLoggerValue.ContextLambda(
            lambda ctx: ctx[StandardTypedLoggerValues.Level].map_absent(
                lambda lvl: logging.getLevelName(lvl.v),
            ),
        )

    #

    class Msg(TypedLoggerValue[str]):
        _default_key = True

    #

    class Caller(TypedLoggerValue[LoggingCaller]):
        pass

    #

    class Tid(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> ta.Union[int, AbsentTypedLoggerValue]:
            if hasattr(threading, 'get_native_id'):
                return threading.get_native_id()
            else:
                return ABSENT_TYPED_LOGGER_VALUE

    class ThreadIdent(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> int:
            return threading.get_ident()

    class ThreadName(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> str:
            return threading.current_thread().name

    #

    class Pid(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> int:
            return os.getpid()

    class ProcessName(DefaultTypedLoggerValue[str]):
        @classmethod
        def _default_value(cls) -> ta.Union[str, AbsentTypedLoggerValue]:
            if (mp := sys.modules.get('multiprocessing')) is None:
                return ABSENT_TYPED_LOGGER_VALUE

            # Errors may occur if multiprocessing has not finished loading yet - e.g. if a custom import hook causes
            # third-party code to run when multiprocessing calls import. See issue 8200 for an example
            try:
                return mp.current_process().name
            except Exception:  # noqa
                return ABSENT_TYPED_LOGGER_VALUE

    #

    class AsyncioTaskName(DefaultTypedLoggerValue[str]):
        @classmethod
        def _default_value(cls) -> ta.Union[str, AbsentTypedLoggerValue]:
            if (asyncio := sys.modules.get('asyncio')) is None:
                return ABSENT_TYPED_LOGGER_VALUE

            try:
                return asyncio.current_task().get_name()
            except Exception:  # noqa
                return ABSENT_TYPED_LOGGER_VALUE


########################################
# ../../../omlish/logs/typed/tests/api.py


##


DEFAULT_TYPED_LOGGER_BINDINGS = FullTypedLoggerBindings(
    TypedLoggerField('time', StandardTypedLoggerValues.Time),
    TypedLoggerField('level', StandardTypedLoggerValues.LevelName),
    TypedLoggerField('msg', StandardTypedLoggerValues.Msg),
)

_ABSENT_TYPED_LOGGER_MSG_PROVIDER = ConstTypedLoggerValueProvider(StandardTypedLoggerValues.Msg, ABSENT_TYPED_LOGGER_VALUE)  # noqa


##


class TypedLogger(ta.Protocol):
    def log(
        self,
        level: LogLevel,
        msg: ta.Union[str, tuple, CanTypedLoggerBinding, None] = None,
        /,
        *items: CanTypedLoggerBinding,
        **kwargs: ta.Union[TypedLoggerFieldValue, ta.Any],
    ) -> None: ...


class TypedLoggerImpl:
    def __init__(
            self,
            bindings: TypedLoggerBindings,
    ) -> None:
        super().__init__()

        self._bindings = bindings

    #

    @ta.overload
    def log_(
            self,
            level: LogLevel,
            msg: ta.Union[str, tuple, CanTypedLoggerBinding, None] = None,
            /,
            *items: CanTypedLoggerBinding,
            **kwargs: ta.Union[TypedLoggerFieldValue, ta.Any],
    ) -> None:
        ...

    @ta.overload
    def log_(
            self,
            level: LogLevel,
            fn: ta.Callable[[], ta.Sequence[ta.Union[str, CanTypedLoggerBinding, None]]],
            /,
    ) -> None:
        ...

    def log_(self, *args, **kwargs):
        # TODO: the fn form forbids additional args / kwargs - strictly a single callable
        raise NotImplementedError

    #

    def log(
            self,
            level: LogLevel,
            msg: ta.Union[str, tuple, CanTypedLoggerBinding, None] = None,
            /,
            *items: CanTypedLoggerBinding,
            **kwargs: ta.Union[TypedLoggerFieldValue, ta.Any],
    ) -> None:
        # TODO: log(INFO, lambda: (...))

        msg_items: ta.Sequence[CanTypedLoggerBinding]
        if msg is None:
            msg_items = (_ABSENT_TYPED_LOGGER_MSG_PROVIDER,)
        elif isinstance(msg, str):
            msg_items = (StandardTypedLoggerValues.Msg(msg),)
        elif isinstance(msg, tuple):
            msg_items = (StandardTypedLoggerValues.Msg(msg[0] % msg[1:]),)
        else:
            msg_items = (_ABSENT_TYPED_LOGGER_MSG_PROVIDER, msg)

        # LoggingCaller.

        bs = FullTypedLoggerBindings(
            self._bindings,
            StandardTypedLoggerValues.TimeNs(time.time_ns()),
            StandardTypedLoggerValues.Level(level),
            *as_typed_logger_bindings(
                *msg_items,
                *items,
                *kwargs.items(),
                add_default_keys=True,
                value_wrapper=self._bindings.value_wrapper_fn,
            ),
            override=True,
        )

        ctx = TypedLoggerContext(bs)

        for k, fv in ctx.bindings.key_map.items():
            print((k, ctx.unwrap_field_value(fv)))
        print()


########################################
# tlog.py


##


@dc.dataclass(frozen=True)
class Thingy:
    s: str


class LoggerValues:
    class Tag(TypedLoggerValue[str]):
        _default_key = True

    class Thingy_(TypedLoggerValue[Thingy]):  # noqa
        _default_key = 'thingy'

    class Thingy2(DefaultTypedLoggerValue[str]):
        _default_key = True

        @classmethod
        def _default_value(cls, thingy: 'LoggerValues.Thingy_') -> str:
            return thingy.v.s + ' - 2'


def _main() -> None:
    tlog = TypedLoggerImpl(FullTypedLoggerBindings(
        DEFAULT_TYPED_LOGGER_BINDINGS,
        TypedLoggerValueWrapper({Thingy}, LoggerValues.Thingy_),
    ))

    for _ in range(2):
        tlog.log(
            logging.INFO,
            'hi',
            LoggerValues.Tag('some tag'),
            ('foo', 'bar'),
            Thingy('wrap me'),  # type: ignore
            LoggerValues.Thingy2,
            barf=True,
        )

        tlog.log(logging.INFO, 'abcd')
        tlog.log(logging.INFO, ('abc %d efg', 420))


if __name__ == '__main__':
    _main()
