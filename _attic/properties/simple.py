import functools
import typing as ta

from .base import Property


T = ta.TypeVar('T')


class ValueNotSetException(ValueError):
    pass


class ValueAlreadySetException(ValueError):
    pass


class SetOnceProperty(Property[T]):

    def __init__(self, attr_name: ta.Optional[str] = None) -> None:
        super().__init__()

        self._attr_name = attr_name or '__%s_%x_value' % (type(self).__name__, id(self))

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return getattr(instance, self._attr_name)
        except AttributeError:
            raise ValueNotSetException

    def __set__(self, instance, value):
        try:
            getattr(instance, self._attr_name)
        except AttributeError:
            setattr(instance, self._attr_name, value)
        else:
            raise ValueAlreadySetException

    def __delete__(self, instance):
        raise TypeError('Operation not supported')


def set_once(attr_name: ta.Optional[str] = None):
    return SetOnceProperty(attr_name)


class ClassProperty(Property[T]):

    def __init__(
            self,
            func: ta.Callable[[ta.Any], T],
    ) -> None:
        super().__init__()

        functools.update_wrapper(ta.cast(ta.Callable, self), func)
        self._func = self._unwrap(func)

    @classmethod
    def _unwrap(cls, fn):
        if isinstance(fn, classmethod):
            return fn.__func__
        return super()._unwrap(fn)

    def __get__(self, obj, cls=None) -> T:
        return self._func(cls)


def class_(fn: ta.Callable[..., T]) -> T:
    return ClassProperty(fn)  # type: ignore
