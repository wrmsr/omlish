import functools
import typing as ta

from .functions import unwrap_func


T = ta.TypeVar('T')

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


def cached_nullary(fn):
    if isinstance(fn, staticmethod):
        return _CachedNullary(fn, value_fn=unwrap_func(fn))  # type: ignore
    scope = classmethod if isinstance(fn, classmethod) else None
    return _CachedNullaryDescriptor(fn, scope)
