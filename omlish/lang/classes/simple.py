import abc
import functools
import threading
import typing as ta

from .restrict import Final
from .restrict import NotInstantiable


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class SimpleMetaDict(dict):
    def update(self, m: ta.Mapping[K, V], **kwargs: V) -> None:  # type: ignore
        for k, v in m.items():
            self[k] = v
        for k, v in kwargs.items():  # type: ignore
            self[k] = v


##


_MARKER_NAMESPACE_KEYS: set[str] | None = None


class _MarkerMeta(abc.ABCMeta):
    def __new__(mcls, name, bases, namespace):
        global _MARKER_NAMESPACE_KEYS

        if _MARKER_NAMESPACE_KEYS is None:
            if not (namespace.get('__module__') == __name__ and name == 'Marker'):
                raise RuntimeError
            _MARKER_NAMESPACE_KEYS = set(namespace)

        else:
            if set(namespace) - _MARKER_NAMESPACE_KEYS:
                raise TypeError('Markers must not include contents. Did you mean to use Namespace?')
            if Final not in bases:
                bases += (Final,)

        return super().__new__(mcls, name, bases, namespace)

    def __instancecheck__(self, instance):
        return instance is self

    def __repr__(cls) -> str:
        return f'<{cls.__name__}>'


class Marker(NotInstantiable, metaclass=_MarkerMeta):
    """A marker."""

    def __bool__(self):
        raise TypeError


##


_SINGLETON_INSTANCE_ATTR = '__singleton_instance__'


def _set_singleton_instance(inst):
    cls = inst.__class__
    if _SINGLETON_INSTANCE_ATTR in cls.__dict__:
        raise TypeError(cls)

    inst.__init__()
    old_init = cls.__init__

    @functools.wraps(old_init)
    def new_init(self):
        if self.__class__ is not cls:
            old_init(self)  # noqa

    setattr(cls, '__init__', new_init)
    setattr(cls, _SINGLETON_INSTANCE_ATTR, inst)

    return inst


class _AnySingleton:
    def __init__(self) -> None:
        try:
            type(self).__dict__[_SINGLETON_INSTANCE_ATTR]
        except KeyError:
            pass
        else:
            raise TypeError(f'Must not re-instantiate singleton {type(self)}')

        super().__init__()

    @ta.final
    def __reduce__(self):
        return (type(self), ())


class Singleton(_AnySingleton):
    @ta.final
    def __new__(cls):
        return cls.__dict__[_SINGLETON_INSTANCE_ATTR]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        _set_singleton_instance(super().__new__(cls))  # noqa


_LAZY_SINGLETON_LOCK = threading.RLock()


class LazySingleton(_AnySingleton):
    @ta.final
    def __new__(cls):
        try:
            return cls.__dict__[_SINGLETON_INSTANCE_ATTR]
        except KeyError:
            pass

        with _LAZY_SINGLETON_LOCK:
            try:
                return cls.__dict__[_SINGLETON_INSTANCE_ATTR]
            except KeyError:
                pass

            return _set_singleton_instance(super().__new__(cls))
