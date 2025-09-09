# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract
from ...lite.reflect import is_union_alias
from ...lite.strings import snake_case
from ...lite.wrappers import update_wrapper_no_annotations


if ta.TYPE_CHECKING:
    from .bindings import TypedLoggerBindings
    from .contexts import TypedLoggerContext


T = ta.TypeVar('T')
U = ta.TypeVar('U')

TypedLoggerValueT = ta.TypeVar('TypedLoggerValueT', bound='TypedLoggerValue')

TypedLoggerValueOrProvider = ta.Union['TypedLoggerValue', 'TypedLoggerValueProvider']  # ta.TypeAlias

AbsentTypedLoggerValue = ta.Type['ABSENT_TYPED_LOGGER_VALUE']  # ta.TypeAlias

TypedLoggerValueOrAbsent = ta.Union['TypedLoggerValue', AbsentTypedLoggerValue]
TypedLoggerValueOrProviderOrAbsent = ta.Union[TypedLoggerValueOrProvider, AbsentTypedLoggerValue]  # ta.TypeAlias

TypedLoggerFieldValue = ta.Union[TypedLoggerValueOrProviderOrAbsent, ta.Type['TypedLoggerValue'], 'TypedLoggerConstFieldValue']  # ta.TypeAlias  # noqa
ResolvedTypedLoggerFieldValue = ta.Union[TypedLoggerValueOrAbsent, 'TypedLoggerConstFieldValue']  # ta.TypeAlias
UnwrappedTypedLoggerFieldValue = ta.Union[TypedLoggerValueOrAbsent, ta.Any]  # ta.TypeAlias


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

    @ta.final
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


class MultiTypedLoggerValue(TypedLoggerValue[T], Abstract):
    """
    Note: There is no DefaultMultiTypedLoggerValue.
    """

    @classmethod
    @abc.abstractmethod
    def merge_values(cls, *values: T) -> T:
        raise NotImplementedError

    #

    def _typed_logger_visit_bindings(self, vst: 'TypedLoggerBindings._Visitor') -> None:  # noqa
        vst.accept_multi_values(((type(self), self),))


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
