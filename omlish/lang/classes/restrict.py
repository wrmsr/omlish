import functools
import typing as ta

from .abstract import Abstract
from .abstract import is_abstract


##


class FinalError(TypeError):

    def __init__(self, _type: type) -> None:
        super().__init__()

        self._type = _type

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._type})'


class Final(Abstract):
    __slots__ = ()

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        abstracts: set[ta.Any] = set()
        for base in cls.__bases__:
            if base is Abstract:
                raise FinalError(base)
            elif base is Final:
                continue
            elif Final in base.__mro__:
                raise FinalError(base)
            else:
                abstracts.update(getattr(base, '__abstractmethods__', []))

        for a in abstracts:
            try:
                v = cls.__dict__[a]
            except KeyError:
                raise FinalError(a) from None
            if is_abstract(v):
                raise FinalError(a)


##


class SealedError(TypeError):

    def __init__(self, _type) -> None:
        super().__init__()

        self._type = _type

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._type})'


class Sealed:
    __slots__ = ()

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        for base in cls.__bases__:
            if base is not Abstract:
                if Sealed in base.__bases__:
                    if cls.__module__ != base.__module__:
                        raise SealedError(base)
        super().__init_subclass__(**kwargs)


class PackageSealed:
    __slots__ = ()

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        for base in cls.__bases__:
            if base is not Abstract:
                if PackageSealed in base.__bases__:
                    pfx = base.__module__.split('.')[:-1]
                    if cls.__module__.split('.')[:len(pfx)] != pfx:
                        raise SealedError(base)
        super().__init_subclass__(**kwargs)


##


class NotInstantiable(Abstract):
    __slots__ = ()

    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


class NotPicklable:
    __slots__ = ()

    @ta.final
    def __reduce__(self) -> ta.NoReturn:
        raise TypeError

    @ta.final
    def __reduce_ex__(self, protocol) -> ta.NoReturn:
        raise TypeError

    @ta.final
    def __getstate__(self) -> ta.NoReturn:
        raise TypeError

    @ta.final
    def __setstate__(self, state) -> ta.NoReturn:
        raise TypeError


##


class NoBool:

    def __bool__(self) -> bool:
        raise TypeError


class _NoBoolDescriptor:

    def __init__(self, fn, instance=None, owner=None) -> None:
        super().__init__()
        self._fn = fn
        self._instance = instance
        self._owner = owner
        functools.update_wrapper(self, fn)

    def __bool__(self) -> bool:
        raise TypeError

    def __get__(self, instance, owner=None):
        if instance is self._instance and owner is self._owner:
            return self
        return _NoBoolDescriptor(self._fn.__get__(instance, owner), instance, owner)

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)


def no_bool(fn):  # noqa
    return _NoBoolDescriptor(fn)
