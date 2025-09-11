import abc
import functools
import typing as ta

from .abstract import Abstract


##


class FinalTypeError(TypeError):
    def __init__(self, _type: type) -> None:
        super().__init__()

        self._type = _type

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._type})'


class Final(Abstract):
    __slots__ = ()

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for base in cls.__bases__:
            if base is Abstract:
                raise FinalTypeError(base)
            elif base is Final:
                continue
            elif Final in base.__mro__:
                raise FinalTypeError(base)

        # Per `ta.final`:
        try:
            cls.__final__ = True  # type: ignore[attr-defined]
        except (AttributeError, TypeError):
            # Skip the attribute silently if it is not writable. AttributeError happens if the object has __slots__ or
            # a read-only property, TypeError if it's a builtin class.
            pass


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

    __sealed_package__: ta.ClassVar[ta.Sequence[str] | None]

    def __init_subclass__(cls, *, sealed_package: ta.Sequence[str] | str | None = None, **kwargs: ta.Any) -> None:
        if PackageSealed in cls.__bases__:
            if sealed_package is not None:
                if isinstance(sealed_package, str):
                    sealed_package = sealed_package.split('.')
                cls.__sealed_package__ = sealed_package
            else:
                cls.__sealed_package__ = cls.__module__.split('.')[:-1]
        elif sealed_package is not None:
            raise TypeError

        for base in cls.__bases__:
            if (
                    base is Abstract or
                    PackageSealed not in base.__bases__
            ):
                continue
            bsp = base.__dict__['__sealed_package__']
            if cls.__module__.split('.')[:len(bsp)] != bsp:
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


##


SENSITIVE_ATTR = '__sensitive__'


class Sensitive:
    __sensitive__ = True


class _AnySensitiveMeta(abc.ABCMeta):
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return hasattr(instance, SENSITIVE_ATTR) or super().__instancecheck__(AnySensitive, instance)

    @classmethod
    def __subclasscheck__(cls, subclass: type) -> bool:
        return hasattr(subclass, SENSITIVE_ATTR) or super().__subclasscheck__(AnySensitive, subclass)


class AnySensitive(NotInstantiable, Final, metaclass=_AnySensitiveMeta):
    pass
