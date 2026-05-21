# ruff: noqa: UP006 UP007 UP037
# @omlish-lite
"""
Obviously inspired by kotlin. This is intended to complement, not compete with, dependency injection: where DI replaces
kwargs, this replaces globals. Or, in more 'coarse' terms: DI is for classes, this is for functions.

Primary intended usecases:
 - logging / metrics
 - marshaling
 - typeclass-y / capability things

Possible additional usecases:
 - 'current_user' and such - at least the dep is explicit (versus just referring to a global cvar)
"""
import contextvars
import functools
import inspect
import types
import typing as ta

from .injectinspect import injection_inspect
from .reflect import get_optional_alias_arg
from .reflect import is_optional_alias


T = ta.TypeVar('T')
U = ta.TypeVar('U')

CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

ContextualParams = ta.Sequence['ContextualParam']  # ta.TypeAlias


##


_CONTEXTUAL_BINDINGS: 'contextvars.ContextVar[ta.Mapping[ta.Any, ta.Any]]' = contextvars.ContextVar(
    'contextual._CONTEXTUAL_BINDINGS',
    default=types.MappingProxyType({}),
)


##


class UnboundContextualError(RuntimeError):
    pass


@ta.final
class NO_CONTEXTUAL_DEFAULT:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


##


def _raise_unbound_contextual_error(*args, **kwargs):
    raise UnboundContextualError


@ta.final
class _UnboundContextualParam:
    def __init__(self, default: ta.Any = NO_CONTEXTUAL_DEFAULT) -> None:
        object.__setattr__(self, '__contextual_default__', default)

    # These make a reasonable attempt to prevent misuse, but it does not attempt to cover all possible accesses (like
    # something like `wrapt` would). In practice the raising paths will only be hit when a function using
    # `contextual_param`'s is not wrapped in `@contextual_wrap()` - which is always a bug.

    def __getattribute__(self, item):
        # Needed by inspect
        if item == '__class__':
            return object.__getattribute__(self, item)

        raise UnboundContextualError

    __setattr__ = _raise_unbound_contextual_error
    __delattr__ = _raise_unbound_contextual_error

    __call__ = _raise_unbound_contextual_error
    __bool__ = _raise_unbound_contextual_error

    __hash__ = _raise_unbound_contextual_error
    __eq__ = _raise_unbound_contextual_error
    __ne__ = _raise_unbound_contextual_error

    __lt__ = _raise_unbound_contextual_error
    __le__ = _raise_unbound_contextual_error
    __gt__ = _raise_unbound_contextual_error
    __ge__ = _raise_unbound_contextual_error

    __getstate__ = _raise_unbound_contextual_error
    __reduce__ = _raise_unbound_contextual_error
    __reduce_ex__ = _raise_unbound_contextual_error

    __str__ = _raise_unbound_contextual_error
    # __repr__ = _raise_unbound_contextual_error  # Needed by inspect
    __format__ = _raise_unbound_contextual_error


@ta.overload
def contextual_param() -> T: ...  # type: ignore[type-var]


@ta.overload
def contextual_param(default: T, /) -> T: ...


def contextual_param(default=NO_CONTEXTUAL_DEFAULT, /):
    return _UnboundContextualParam(default)


##


@ta.final
class ContextualParam:
    def __init__(
            self,
            name: str,
            key: ta.Any,
            *,
            default: ta.Any = NO_CONTEXTUAL_DEFAULT,
    ) -> None:
        self._name = name
        self._key = key
        self._default = default

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'name={self._name!r}, '
            f'key={self._key!r}, '
            f'default={self._default!r})'
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def key(self) -> ta.Any:
        return self._key

    @property
    def default(self) -> ta.Any:
        return self._default


def inspect_contextual_params(
        fn: ta.Any,
        *,
        raw_optional: bool = False,
) -> ContextualParams:
    insp = injection_inspect(fn)

    lst: list[ContextualParam] = []

    for p in insp.signature.parameters.values():
        if (pd := p.default) is inspect.Signature.empty or not isinstance(pd, _UnboundContextualParam):
            continue

        # 3.8 inspect.signature doesn't eval_str but typing.get_type_hints does, so prefer that.
        ann = insp.type_hints.get(p.name, p.annotation)

        if (
                not raw_optional and
                is_optional_alias(ann)
        ):
            ann = get_optional_alias_arg(ann)

        lst.append(ContextualParam(
            p.name,
            ann,
            default=object.__getattribute__(pd, '__contextual_default__'),
        ))

    return tuple(lst)


##


@ta.final
class _ContextualWrapper(ta.Generic[T]):
    def __init__(self, fn: ta.Callable[..., T]) -> None:
        self._fn = fn

        def _params() -> ContextualParams:
            nonlocal _params
            params = self.params()
            _params = lambda: params
            return params

        @functools.wraps(fn)
        def wrapped(*args: ta.Any, **kwargs: ta.Any) -> T:
            bindings = _CONTEXTUAL_BINDINGS.get()

            p: ContextualParam
            nonlocal _params  # noqa
            for p in _params():
                if (pn := p._name) in kwargs:  # noqa
                    continue
                try:
                    kwargs[pn] = bindings[p._key]  # noqa
                except KeyError:
                    if (pd := p._default) is not NO_CONTEXTUAL_DEFAULT:  # noqa
                        kwargs[pn] = pd
                    else:
                        raise UnboundContextualError(fn, p) from None

            return fn(*args, **kwargs)

        self._wrapped = wrapped

    #

    _params: ContextualParams

    def params(self) -> ContextualParams:
        try:
            return self._params
        except AttributeError:
            pass
        self._params = params = inspect_contextual_params(self._fn)
        return params

    #

    _wrapped: ta.Callable[..., T]

    @property
    def wrapped(self) -> ta.Callable[..., T]:
        return self._wrapped


class ContextualWrapping(ta.Protocol):
    @ta.overload
    def __call__(self, ty: ta.Type[T]) -> ta.Type[T]: ...

    @ta.overload
    def __call__(self, fn: CallableT) -> CallableT: ...


def contextual_wrap() -> ContextualWrapping:
    def inner(obj):
        if isinstance(obj, type):
            wr_init = _ContextualWrapper(getattr(obj, '__init__')).wrapped
            setattr(obj, '__init__', wr_init)
            wr_init.__qualname__ = f'{obj.__qualname__}.__init__'
            return obj

        elif callable(obj):
            return _ContextualWrapper(obj).wrapped

        else:
            raise TypeError(f'Cannot wrap non-callable object: {obj!r}')

    return inner  # noqa


##


@ta.final
class _ContextualBinder:
    def __init__(self, bindings: ta.Mapping[ta.Any, ta.Any]) -> None:
        self._bindings = bindings

    _token: contextvars.Token

    def __enter__(self) -> None:
        self._token = _CONTEXTUAL_BINDINGS.set({
            **_CONTEXTUAL_BINDINGS.get(),
            **self._bindings,
        })

    def __exit__(self, et, e, tb) -> None:
        _CONTEXTUAL_BINDINGS.reset(self._token)


def contextual_bind(bindings: ta.Mapping[ta.Any, ta.Any]) -> ta.ContextManager[None]:
    return _ContextualBinder(bindings)


##


@ta.overload
def contextual_get(key: ta.Type[T], /) -> T: ...


@ta.overload
def contextual_get(key: ta.Type[T], default: ta.Union[T, U], /) -> ta.Union[T, U]: ...


def contextual_get(key, default=NO_CONTEXTUAL_DEFAULT, /):
    try:
        return _CONTEXTUAL_BINDINGS.get()[key]
    except KeyError:
        if default is not NO_CONTEXTUAL_DEFAULT:
            return default
        raise UnboundContextualError(key) from None
