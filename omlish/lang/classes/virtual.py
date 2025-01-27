import abc
import types
import typing as ta

from .abstract import make_abstract
from .restrict import Final
from .restrict import NotInstantiable


T = ta.TypeVar('T')
Ty = ta.TypeVar('Ty', bound=type)


##


def _make_not_instantiable():
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError(cls)

    def __init__(self, *args, **kwargs):  # noqa
        raise TypeError(self)

    return {
        '__new__': __new__,
        '__initT__': __init__,
    }


class _VirtualMeta(abc.ABCMeta):
    def __new__(mcls, name, bases, namespace):
        if 'Virtual' not in globals():
            return super().__new__(mcls, name, bases, namespace)
        if Virtual not in bases:
            raise TypeError

        for k, v in list(namespace.items()):
            absv = make_abstract(v)
            if absv is not v:
                namespace[k] = absv

        reqs = {
            k: v
            for k, v in namespace.items()
            if getattr(v, '__isabstractmethod__', False)
        }

        user_subclasshook = namespace.pop('__subclasshook__', None)

        def get_missing_reqs(cls):
            reqset = set(reqs)
            for mro_cls in cls.__mro__:
                reqset -= set(mro_cls.__dict__)
            return reqset

        def __subclasshook__(cls, subclass):  # noqa
            if cls is not kls:
                return super(kls, cls).__subclasshook__(subclass)  # type: ignore
            if get_missing_reqs(subclass):
                return False
            if user_subclasshook is not None:
                ret = user_subclasshook(cls, subclass)
            else:
                ret = super(kls, cls).__subclasshook__(subclass)  # type: ignore
            return True if ret is NotImplemented else ret

        namespace['__subclasshook__'] = classmethod(__subclasshook__)

        namespace.update(_make_not_instantiable())

        kls = ta.cast(
            type,
            super().__new__(
                abc.ABCMeta,
                name,
                tuple(b for b in bases if b is not Virtual),
                namespace,
            ),
        )
        return kls


class Virtual(metaclass=_VirtualMeta):
    """Like Protocol but supports more than just methods."""


def virtual_check(virtual: type) -> ta.Callable[[Ty], Ty]:
    def inner(cls):
        if not issubclass(cls, virtual):
            raise TypeError(cls)
        return cls
    # if not issubclass(type(virtual), _VirtualMeta):
    #     raise TypeError(virtual)
    return inner


##


class Descriptor(Virtual):
    def __get__(self, instance, owner=None):
        raise NotImplementedError


class Picklable(Virtual):
    def __getstate__(self):
        raise NotImplementedError

    def __setstate__(self, state):
        raise NotImplementedError


##


class Callable(NotInstantiable, Final, ta.Generic[T]):
    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        raise TypeError

    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return callable(instance)

    @classmethod
    def __subclasscheck__(cls, subclass: type) -> bool:
        if not hasattr(subclass, '__call__'):  # noqa
            return False
        call = subclass.__call__
        if isinstance(call, types.MethodWrapperType) and call.__self__ is subclass:
            return False
        return True
