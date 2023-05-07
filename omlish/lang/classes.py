"""
TODO:
 - final check
"""
import abc
import typing as ta


_DISABLE_CHECKS = False


##


class Abstract(abc.ABC):
    __slots__ = ()

    def __forceabstract__(self):
        raise TypeError

    setattr(__forceabstract__, '__isabstractmethod__', True)

    def __init_subclass__(cls, **kwargs) -> None:
        if Abstract in cls.__bases__:
            cls.__forceabstract__ = Abstract.__forceabstract__  # type: ignore
        else:
            cls.__forceabstract__ = False  # type: ignore

        super().__init_subclass__(**kwargs)  # type: ignore

        if not _DISABLE_CHECKS and Abstract not in cls.__bases__:
            ams = {a for a, o in cls.__dict__.items() if is_abstract_method(o)}
            seen = set(cls.__dict__)
            for b in cls.__bases__:
                ams.update(set(getattr(b, '__abstractmethods__', [])) - seen)
                seen.update(dir(b))
            if ams:
                raise TypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods'
                    f'{", ".join(map(str, sorted(ams)))}'
                )


abstract = abc.abstractmethod


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, '__isabstractmethod__', False))


def is_abstract_class(obj: ta.Any) -> bool:
    if bool(getattr(obj, '__abstractmethods__', [])):
        return True
    if isinstance(obj, type):
        if Abstract in obj.__bases__:
            return True
        if (
                Abstract in obj.__mro__
                and getattr(obj.__dict__.get('__forceabstract__', None), '__isabstractmethod__', False)
        ):
            return True
    return False


def is_abstract(obj: ta.Any) -> bool:
    return is_abstract_method(obj) or is_abstract_class(obj)


##


class FinalException(TypeError):

    def __init__(self, _type: ta.Type) -> None:
        super().__init__()

        self._type = _type

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._type})'


class Final(Abstract):
    __slots__ = ()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        abstracts: ta.Set[ta.Any] = set()
        for base in cls.__bases__:
            if base is Abstract:
                raise FinalException(base)
            elif base is Final:
                continue
            elif Final in base.__mro__:
                raise FinalException(base)
            else:
                abstracts.update(getattr(base, '__abstractmethods__', []))

        for a in abstracts:
            try:
                v = cls.__dict__[a]
            except KeyError:
                raise FinalException(a)
            if is_abstract(v):
                raise FinalException(a)


##

class SealedException(TypeError):

    def __init__(self, _type) -> None:
        super().__init__()

        self._type = _type

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._type})'


class Sealed:
    __slots__ = ()

    def __init_subclass__(cls, **kwargs) -> None:
        for base in cls.__bases__:
            if base is not Abstract:
                if Sealed in base.__bases__:
                    if cls.__module__ != base.__module__:
                        raise SealedException(base)
        super().__init_subclass__(**kwargs)  # type: ignore


class PackageSealed:
    __slots__ = ()

    def __init_subclass__(cls, **kwargs) -> None:
        for base in cls.__bases__:
            if base is not Abstract:
                if PackageSealed in base.__bases__:
                    if cls.__module__.split('.')[:-1] != base.__module__.split('.')[:-1]:
                        raise SealedException(base)
        super().__init_subclass__(**kwargs)  # type: ignore


##


class NotInstantiable(Abstract):
    __slots__ = ()

    def __new__(cls, *args, **kwargs) -> ta.NoReturn:  # type: ignore
        raise TypeError


class NotPicklable:
    __slots__ = ()

    def __getstate__(self) -> ta.NoReturn:
        raise TypeError

    def __setstate__(self, state) -> ta.NoReturn:
        raise TypeError


##


class _Namespace(Final):

    def __mro_entries__(self, bases, **kwargs):
        return (Final, NotInstantiable)


Namespace: type = _Namespace()  # type: ignore
#


##


_MARKER_NAMESPACE_KEYS: ta.Optional[ta.Set[str]] = None


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

    __slots__ = ()
