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
