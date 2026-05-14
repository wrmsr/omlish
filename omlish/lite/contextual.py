# ruff: noqa: UP037
# @omlish-lite
import contextvars
import functools
import inspect
import types
import typing as ta

from .injectinspect import injection_inspect


T = ta.TypeVar('T')

ContextualParams = ta.Sequence['ContextualParam']  # ta.TypeAlias


##


_CONTEXTUAL_BINDINGS: 'contextvars.ContextVar[ta.Mapping[ta.Any, ta.Any]]' = contextvars.ContextVar(
    'contextual._CONTEXTUAL_BINDINGS',
    default=types.MappingProxyType({}),
)


##


class UnboundContextualParamError(RuntimeError):
    pass


class _UnboundContextualParam:
    def __getattr__(self, name):
        raise UnboundContextualParamError


@ta.final
class NO_CONTEXTUAL_DEFAULT:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


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
        return f'{self.__class__.__name__}(name={self._name!r}, key={self._key!r}, default={self._default!r})'

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
                        raise UnboundContextualParamError(fn, p) from None

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


def contextual_wrap() -> ta.Callable[[ta.Callable[..., T]], ta.Callable[..., T]]:
    def inner(fn):
        return _ContextualWrapper(fn).wrapped

    return inner


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
