import functools
import sys
import types
import typing as ta

from .descriptors import is_method_descriptor


T = ta.TypeVar('T')
U = ta.TypeVar('U')


_MISSING = object()


_CLS_DCT_ATTR_SETS = [
    {
        '__module__',
        '__qualname__',
    },
    {
        '__all__',
    },
]


def _skip_cls_dct_frames(f: types.FrameType) -> types.FrameType:
    if sys.implementation.name == 'pypy':
        if f.f_code is functools.partial.__call__.__code__:
            return _skip_cls_dct_frames(f.f_back)  # type: ignore

    return f


def is_possibly_cls_dct(dct: ta.Mapping[str, ta.Any]) -> bool:
    return any(all(a in dct for a in s) for s in _CLS_DCT_ATTR_SETS)


class ClassDctFn:

    def __init__(self, fn: ta.Callable, offset: ta.Optional[int] = None, *, wrap=True) -> None:
        super().__init__()

        self._fn = fn
        self._offset = offset if offset is not None else 1

        if wrap:
            functools.update_wrapper(self, fn)

    def __get__(self, instance, owner=None):
        return type(self)(self._fn.__get__(instance, owner), self._offset)

    def __call__(self, *args, **kwargs):
        try:
            cls_dct = kwargs.pop('cls_dct')
        except KeyError:
            f = sys._getframe(self._offset)  # noqa
            cls_dct = _skip_cls_dct_frames(f).f_locals
        if not is_possibly_cls_dct(cls_dct):
            raise TypeError(cls_dct)
        return self._fn(cls_dct, *args, **kwargs)


def cls_dct_fn(offset=1, *, wrap=True):
    def outer(fn):
        return ClassDctFn(fn, offset, wrap=wrap)
    return outer


def is_lambda(f: ta.Any) -> bool:
    l = lambda: 0
    return isinstance(f, type(l)) and f.__name__ == l.__name__


def maybe_call(obj: ta.Any, att: str, *args, default: ta.Any = None, **kwargs) -> ta.Any:
    try:
        fn = getattr(obj, att)
    except AttributeError:
        return default
    else:
        return fn(*args, **kwargs)


def unwrap_func(fn: ta.Callable) -> ta.Callable:
    while True:
        if is_method_descriptor(fn):
            fn = fn.__func__  # type: ignore
        elif isinstance(fn, functools.partial):
            fn = fn.func
        else:
            nxt = getattr(fn, '__wrapped__', None)
            if not callable(nxt):
                return fn
            elif nxt is fn:
                raise TypeError(fn)
            fn = nxt


class _CachedNullary(ta.Generic[T]):

    def __init__(
            self,
            fn: ta.Callable[[], T],
            *,
            value: ta.Any = _MISSING,
            value_fn: ta.Optional[ta.Callable[[], T]] = None,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._value = value
        self._value_fn = value_fn if value_fn is not None else fn
        functools.update_wrapper(self, fn)

    def reset(self) -> None:
        self._value = _MISSING

    def __bool__(self) -> bool:
        raise TypeError

    def __call__(self) -> T:
        if self._value is not _MISSING:
            return self._value  # type: ignore
        value = self._value = self._value_fn()
        return value


class _CachedNullaryDescriptor(_CachedNullary[T]):

    def __init__(
            self,
            fn: ta.Callable[[], T],
            scope: ta.Any,
            *,
            instance: ta.Any = None,
            owner: ta.Any = None,
            name: ta.Optional[str] = None,
            **kwargs
    ) -> None:
        super().__init__(fn, **kwargs)

        self._scope = scope
        self._instance = instance
        self._owner = owner
        self._name = name if name is not None else unwrap_func(fn).__name__

    def __get__(self, instance, owner=None):
        scope = self._scope
        if owner is self._owner and (instance is self._instance or scope is classmethod):
            return self
        fn = self._fn
        name = self._name
        bound = self.__class__(
            fn,
            scope,
            instance=instance,
            owner=owner,
            value=_MISSING if scope is classmethod else self._value,
            name=name,
            value_fn=fn.__get__(instance, owner),
        )
        if scope is classmethod and owner is not None:
            setattr(owner, name, bound)
        elif instance is not None:
            instance.__dict__[name] = bound
        return bound


def cached_nullary(fn: ta.Callable[[], T]) -> ta.Callable[[], T]:
    if isinstance(fn, staticmethod):
        return _CachedNullary(fn, value_fn=unwrap_func(fn))  # type: ignore
    scope = classmethod if isinstance(fn, classmethod) else None
    return _CachedNullaryDescriptor(fn, scope)


def raise_(exc: ta.Union[Exception, ta.Type[Exception]]) -> ta.NoReturn:
    raise exc


def try_(
        exc: ta.Union[ta.Type[Exception], ta.Iterable[ta.Type[Exception]]] = Exception,
        default: ta.Optional[T] = None,
) -> ta.Callable[..., T]:
    def outer(fn):
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exct:
                return default
        return inner
    exct = (exc,) if isinstance(exc, type) else tuple(exc)
    return outer


def recurse(fn: ta.Callable[..., T], *args, **kwargs) -> T:
    def rec(*args, **kwargs) -> T:
        return fn(rec, *args, **kwargs)
    return rec(*args, **kwargs)


def optional_of(fn: ta.Callable[[T], U]) -> ta.Callable[[ta.Optional[T]], ta.Optional[U]]:
    @functools.wraps(fn)
    def inner(o):
        if o is None:
            return None
        else:
            return fn(o)
    return inner


def identity(obj: T) -> T:
    return obj


class constant(ta.Generic[T]):  # noqa

    def __init__(self, obj: T) -> None:
        super().__init__()

        self._obj = obj

    def __call__(self) -> T:
        return self._obj


def is_none(o: ta.Any) -> bool:
    return o is None


def is_not_none(o: ta.Any) -> bool:
    return o is not None


def cmp(l: ta.Any, r: ta.Any) -> int:
    return int(l > r) - int(l < r)


try:
    from .._ext.cy import lang as _cy_lang
except ImportError:
    pass
else:
    for _att in {
        'constant',
        'identity',
        'is_none',
        'is_not_none',
        'cmp',
    }:
        globals()[_att] = getattr(_cy_lang, _att)
