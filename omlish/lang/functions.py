import dataclasses as dc
import functools
import time
import types
import typing as ta


F = ta.TypeVar('F')
T = ta.TypeVar('T')
P = ta.ParamSpec('P')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


##


def is_lambda(f: ta.Any) -> bool:
    l = lambda: 0
    return isinstance(f, type(l)) and f.__name__ == l.__name__


##


def call_with(fn: ta.Any, *args: ta.Any, **kwargs: ta.Any) -> ta.Callable[[T], T]:
    def inner(obj):
        fn(obj, *args, **kwargs)
        return obj

    return inner


def maybe_call(obj: ta.Any, att: str, *args, default: ta.Any = None, **kwargs: ta.Any) -> ta.Any:
    try:
        fn = getattr(obj, att)
    except AttributeError:
        return default
    else:
        return fn(*args, **kwargs)


def recurse(fn: ta.Callable[..., T], *args, **kwargs) -> T:
    def rec(*args, **kwargs) -> T:
        return fn(rec, *args, **kwargs)

    return rec(*args, **kwargs)


##


def raise_(o: BaseException) -> ta.NoReturn:
    raise o


def raising(o: BaseException) -> ta.Callable[..., ta.NoReturn]:
    def inner(*args, **kwargs):
        raise o

    return inner


def try_(
        fn: ta.Callable[P, T],
        exc: type[Exception] | ta.Iterable[type[Exception]] = Exception,
        default: T | None = None,
) -> ta.Callable[P, T]:
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exct:
            return default

    exct = (exc,) if isinstance(exc, type) else tuple(exc)
    return inner


def finally_(fn: ta.Callable[P, T], fin: ta.Callable) -> ta.Callable[P, T]:
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            fin()

    return inner


##


def identity(obj: T) -> T:
    return obj


def opt_fn(fn: ta.Callable[[F], T]) -> ta.Callable[[F | None], T | None]:
    @functools.wraps(fn)
    def inner(v: F | None) -> T | None:
        if v is not None:
            return fn(v)
        else:
            return None

    return inner


##


class _constant(ta.Generic[T]):  # noqa
    def __init__(self, obj: T) -> None:
        super().__init__()

        self._obj = obj


class constant(_constant[T]):  # noqa
    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        return self._obj


class nullary_constant(_constant[T]):  # noqa
    def __call__(self) -> T:
        return self._obj


##


def is_none(o: ta.Any) -> bool:
    return o is None


def is_not_none(o: ta.Any) -> bool:
    return o is not None


def isinstance_of(class_or_tuple: ta.Any) -> ta.Callable[[ta.Any], bool]:
    return lambda o: isinstance(o, class_or_tuple)


def issubclass_of(class_or_tuple: ta.Any) -> ta.Callable[[ta.Any], bool]:
    return lambda o: issubclass(o, class_or_tuple)


def strict_eq(l: ta.Any, r: ta.Any) -> bool:
    return type(l) is type(r) and l == r


##


class VoidError(Exception):
    pass


class Void:
    def __new__(cls, *args: ta.Any, **kwargs: ta.Any) -> None:  # type: ignore  # noqa
        raise VoidError

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        raise VoidError


def void(*args: ta.Any, **kwargs: ta.Any) -> ta.NoReturn:
    raise VoidError


##


def as_async(fn: ta.Callable[P, T]) -> ta.Callable[P, ta.Awaitable[T]]:
    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return inner


##


_MISSING = object()


def periodically(
        fn: CallableT,
        interval_s: float,
        initial: ta.Any = _MISSING,
        *,
        include_runtime: bool = False,
        clock: ta.Callable[[], float] = time.monotonic,
) -> CallableT:
    nxt = clock() + interval_s
    ret = initial

    @functools.wraps(fn)
    def inner(*args, **kwargs):
        nonlocal nxt, ret
        if clock() >= nxt or ret is _MISSING:
            if include_runtime:
                nxt = clock() + interval_s
            ret = fn(*args, **kwargs)
            if not include_runtime:
                nxt = clock() + interval_s
        return ret

    return inner  # type: ignore


##


@dc.dataclass(init=False)
class Args:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]

    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()

        self.args = args
        self.kwargs = kwargs

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs)

    def update(self, *args: ta.Any, **kwargs: ta.Any) -> 'Args':
        return Args(
            *self.args,
            *args,
            **{
                **self.kwargs,
                **kwargs,
            },
        )

    def __call__(self, fn: ta.Callable[..., T]) -> T:
        return fn(*self.args, **self.kwargs)


##


def coalesce(*vs: T | None) -> T:
    for v in vs:
        if v is not None:
            return v
    raise ValueError('No value given')


def opt_coalesce(*vs: T | None) -> T | None:
    for v in vs:
        if v is not None:
            return v
    return None


##


def cond_kw(cond: ta.Callable[[T], bool], **kwargs: T) -> dict[str, T]:
    return {k: v for k, v in kwargs.items() if cond(v)}


def opt_kw(**kwargs: T | None) -> dict[str, T]:
    return {k: v for k, v in kwargs.items() if v is not None}


def truthy_kw(**kwargs: T) -> dict[str, T]:
    return {k: v for k, v in kwargs.items() if v}


##


def new_function(
        # a code object
        code: types.CodeType,

        # the globals dictionary
        globals: dict,  # noqa

        # a string that overrides the name from the code object
        name: str | None = None,

        # a tuple that specifies the default argument values
        argdefs: tuple | None = None,

        # a tuple that supplies the bindings for free variables
        closure: tuple | None = None,

        # # a dictionary that specifies the default keyword argument values
        # kwdefaults: dict | None = None,
) -> types.FunctionType:
    return types.FunctionType(
        code=code,
        globals=globals,
        name=name,
        argdefs=argdefs,
        closure=closure,
        # kwdefaults=kwdefaults,
    )


def new_function_kwargs(f: types.FunctionType) -> dict[str, ta.Any]:
    return dict(
        code=f.__code__,
        globals=f.__globals__,  # noqa
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
        # kwdefaults=f.__kwdefaults__,
    )
