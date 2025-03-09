import abc
import functools
import typing as ta

from ..attrs import transient_getattr
from ..attrs import transient_setattr
from ..classes.abstract import Abstract


_IGNORE = object()


##


class _CachedProperty(property, Abstract):
    def __init__(
            self,
            fn,
            *,
            name=None,
            ignore_if=lambda _: False,
    ):
        if isinstance(fn, property):
            fn = fn.fget

        super().__init__(fn)

        self._fn = fn
        self._ignore_if = ignore_if

        self._name = name

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = name

    @abc.abstractmethod
    def _instance_get(self, instance: ta.Any) -> tuple[ta.Any, bool]:
        raise NotImplementedError

    @abc.abstractmethod
    def _instance_set(self, instance: ta.Any, value: ta.Any) -> None:
        raise NotImplementedError

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self._name is None:
            raise TypeError(self)

        value, ok = self._instance_get(instance)
        if ok:
            return value

        value = self._fn.__get__(instance, owner)()
        if value is _IGNORE:
            return None

        self._instance_set(instance, value)
        return value

    def __set__(self, instance, value):
        if self._ignore_if(value):
            return

        ev, ok = self._instance_get(instance)
        if ok and ev == value:
            return

        raise TypeError(self._name)

    def __delete__(self, instance):
        raise TypeError


#


class _DictCachedProperty(_CachedProperty):
    def _instance_get(self, instance: ta.Any) -> tuple[ta.Any, bool]:
        try:
            value = instance.__dict__[self._name]
        except KeyError:
            return None, False
        else:
            return value, True

    def _instance_set(self, instance: ta.Any, value: ta.Any) -> None:
        instance.__dict__[self._name] = value


#


class _TransientCachedProperty(_CachedProperty):
    def _instance_get(self, instance: ta.Any) -> tuple[ta.Any, bool]:
        try:
            value = transient_getattr(instance, self._name)
        except AttributeError:
            return None, False
        else:
            return value, True

    def _instance_set(self, instance: ta.Any, value: ta.Any) -> None:
        transient_setattr(instance, self._name, value)


#


def cached_property(fn=None, *, transient=False, **kwargs):  # noqa
    if fn is None:
        return functools.partial(cached_property, transient=transient, **kwargs)
    if transient:
        return _TransientCachedProperty(fn, **kwargs)
    else:
        return _DictCachedProperty(fn, **kwargs)
