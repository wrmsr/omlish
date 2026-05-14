# ruff: noqa: UP006 UP007 UP037
# @omlish-lite
import contextvars
import functools
import inspect
import types
import typing as ta

from .injectinspect import injection_inspect


T = ta.TypeVar('T')
U = ta.TypeVar('U')

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


class _UnboundContextualParam:
    def __getattr__(self, name):
        raise UnboundContextualError


@ta.final
class _DeclaredContextualParam:
    def __init__(self, default: ta.Any = NO_CONTEXTUAL_DEFAULT) -> None:
        self._default = default


@ta.overload
def contextual_param() -> T:  # type: ignore[type-var]
    ...


@ta.overload
def contextual_param(default: T, /) -> T:
    ...


def contextual_param(default=NO_CONTEXTUAL_DEFAULT, /):
    return _DeclaredContextualParam(default)


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


def inspect_contextual_params(fn: ta.Any) -> ContextualParams:
    insp = injection_inspect(fn)

    lst: list[ContextualParam] = []

    for p in insp.signature.parameters.values():
        if (pd := p.default) is inspect.Signature.empty or not isinstance(pd, _DeclaredContextualParam):
            continue

        lst.append(ContextualParam(
            p.name,
            insp.type_hints[p.name],
            default=pd._default,  # noqa
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
    def __call__(self, fn: ta.Callable[..., T]) -> ta.Callable[..., T]: ...

    def __call__(self, obj): ...


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
def contextual_get(key: ta.Type[T], /) -> T:
    ...


@ta.overload
def contextual_get(key: ta.Type[T], default: ta.Union[T, U], /) -> ta.Union[T, U]:
    ...


def contextual_get(key, default=NO_CONTEXTUAL_DEFAULT, /):
    try:
        return _CONTEXTUAL_BINDINGS.get()[key]
    except KeyError:
        if default is not NO_CONTEXTUAL_DEFAULT:
            return default
        raise UnboundContextualError(key) from None
