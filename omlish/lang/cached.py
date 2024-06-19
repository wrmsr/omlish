import functools
import typing as ta

from .functions import unwrap_func


T = ta.TypeVar('T')

_IGNORE = object()
_MISSING = object()


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
            return self._value
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


def cached_nullary(fn):
    if isinstance(fn, staticmethod):
        return _CachedNullary(fn, value_fn=unwrap_func(fn))
    scope = classmethod if isinstance(fn, classmethod) else None
    return _CachedNullaryDescriptor(fn, scope)


##


class _CachedProperty:
    def __init__(self, fn, *, name=None, ignore_if=lambda _: False, clear_on_init=False):
        super().__init__()
        if isinstance(fn, property):
            fn = fn.fget
        self._fn = fn
        self._ignore_if = ignore_if
        self._name = name
        self._clear_on_init = clear_on_init

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self._name is None:
            raise TypeError(self)
        try:
            return instance.__dict__[self._name]
        except KeyError:
            pass
        value = self._fn.__get__(instance, owner)()
        if value is _IGNORE:
            return None
        instance.__dict__[self._name] = value
        return value

    def __set__(self, instance, value):
        if self._ignore_if(value):
            return
        if instance.__dict__[self._name] == value:
            return
        raise TypeError(self._name)


def cached_property(fn=None, **kwargs):
    if fn is None:
        return functools.partial(cached_property, **kwargs)
    return _CachedProperty(fn, **kwargs)
