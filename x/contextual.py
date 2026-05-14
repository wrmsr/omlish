"""
lite:
 - contextual_param, contextual_wrap, contextual_bind
 - no ta.ParamSpec
"""
import contextvars
import functools
import inspect
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')

Params: ta.TypeAlias = ta.Sequence['Param']


##


_BINDINGS: contextvars.ContextVar[ta.Mapping[ta.Any, ta.Any]] = contextvars.ContextVar('contextual._BINDINGS', default={})  # noqa


##


class UnboundParamError(RuntimeError):
    pass


class _UnboundParam:
    def __getattr__(self, name):
        raise UnboundParamError


@ta.final
class NO_DEFAULT:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


@ta.final
class _DeclaredParam:
    def __init__(self, default: ta.Any = NO_DEFAULT) -> None:
        self._default = default


@ta.overload
def param() -> T:  # type: ignore[type-var]
    ...


@ta.overload
def param(default: T, /) -> T:
    ...


def param(default=NO_DEFAULT, /):
    return _DeclaredParam(default)


##


@ta.final
class Param:
    def __init__(
            self,
            name: str,
            key: ta.Any,
            *,
            default: ta.Any = NO_DEFAULT,
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


def inspect_params(fn: ta.Any) -> Params:
    sig = inspect.signature(fn)
    th = ta.get_type_hints(fn)

    lst: list[Param] = []

    for p in sig.parameters.values():
        if (pd := p.default) is inspect.Signature.empty or not isinstance(pd, _DeclaredParam):
            continue

        lst.append(Param(
            p.name,
            th[p.name],
            default=pd._default,  # noqa
        ))

    return tuple(lst)


##


@ta.final
class _Wrapper(ta.Generic[P, T]):
    def __init__(self, fn: ta.Callable[P, T]) -> None:
        self._fn = fn

        def _params() -> Params:
            nonlocal _params
            params = self.params()
            _params = lambda: params
            return params

        @functools.wraps(fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            bindings = _BINDINGS.get()

            p: Param
            nonlocal _params
            for p in _params():
                if (pn := p._name) in kwargs:  # noqa
                    continue
                try:
                    kwargs[pn] = bindings[p._key]  # noqa
                except KeyError:
                    if (pd := p._default) is not NO_DEFAULT:  # noqa
                        kwargs[pn] = pd
                    else:
                        raise UnboundParamError(fn, p) from None

            return fn(*args, **kwargs)

        self._wrapped = wrapped

    #

    _params: Params

    def params(self) -> Params:
        try:
            return self._params
        except AttributeError:
            pass
        self._params = params = inspect_params(self._fn)
        return params

    #

    _wrapped: ta.Callable[P, T]

    @property
    def wrapped(self) -> ta.Callable[P, T]:
        return self._wrapped


def wrap() -> ta.Callable[[ta.Callable[P, T]], ta.Callable[P, T]]:
    def inner(fn):
        return _Wrapper(fn).wrapped

    return inner


##


@ta.final
class _Binder:
    def __init__(self, bindings: ta.Mapping[ta.Any, ta.Any]) -> None:
        self._bindings = bindings

    _token: contextvars.Token

    def __enter__(self) -> None:
        self._token = _BINDINGS.set({
            **_BINDINGS.get(),
            **self._bindings,
        })

    def __exit__(self, et, e, tb) -> None:
        _BINDINGS.reset(self._token)


def bind(bindings: ta.Mapping[ta.Any, ta.Any]) -> ta.ContextManager[None]:
    return _Binder(bindings)
