import functools
import typing as ta

from .functions import unwrap_func


P = ta.ParamSpec('P')
T = ta.TypeVar('T')

_IGNORE = object()


def _cache_key(*args, **kwargs):
    return (args, tuple(sorted(kwargs.items())))


class _CachedFunction(ta.Generic[T]):

    def __init__(
            self,
            fn: ta.Callable[P, T],
            *,
            values: dict | None = None,
            value_fn: ta.Optional[ta.Callable[P, T]] = None,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._values = values if values is not None else {}
        self._value_fn = value_fn if value_fn is not None else fn
        functools.update_wrapper(self, fn)

    def reset(self) -> None:
        self._values = {}

    def __bool__(self) -> bool:
        raise TypeError

    def __call__(self, *args, **kwargs) -> T:
        k = _cache_key(*args, **kwargs)
        try:
            return self._values[k]
        except KeyError:
            pass
        value = self._value_fn(*args, **kwargs)
        self._values[k] = value
        return value


class _CachedFunctionDescriptor(_CachedFunction[T]):

    def __init__(
            self,
            fn: ta.Callable[P, T],
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
            # values=None if scope is classmethod else self._values,
            name=name,
            value_fn=fn.__get__(instance, owner),
        )
        if scope is classmethod and owner is not None:
            setattr(owner, name, bound)
        elif instance is not None:
            instance.__dict__[name] = bound
        return bound


def cached_function(fn=None, **kwargs):
    if fn is None:
        return functools.partial(cached_function, **kwargs)
    if isinstance(fn, staticmethod):
        return _CachedFunction(fn, value_fn=unwrap_func(fn), **kwargs)
    scope = classmethod if isinstance(fn, classmethod) else None
    return _CachedFunctionDescriptor(fn, scope)


cached_nullary = cached_function


##


class _CachedProperty:
    def __init__(
            self,
            fn,
            *,
            name=None,
            ignore_if=lambda _: False,
            clear_on_init=False,
    ):
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
