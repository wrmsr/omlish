"""
TODO:
 - final check
"""
import abc
import typing as ta


##


class NotInstantiable(abc.ABC):
    __slots__ = ()

    def __new__(cls, *args, **kwargs) -> ta.NoReturn:  # type: ignore
        raise TypeError


##


class Final(abc.ABC):
    pass


##


class _Namespace(Final):

    def __mro_entries__(self, bases, **kwargs):
        return (Final, NotInstantiable)


Namespace: type = _Namespace()  # type: ignore

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


##


_DISABLE_CHECKS = False


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
