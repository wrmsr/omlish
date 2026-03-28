import abc
import functools
import typing as ta

from .. import check
from .. import lang


K = ta.TypeVar('K')


##


@functools.total_ordering
class Key(lang.Sealed, lang.Abstract, ta.Generic[K]):
    @property
    @abc.abstractmethod
    def k(self) -> K:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def __lt__(self, other: object) -> bool:
        raise NotImplementedError


##


@ta.final
class _Key(Key[K], lang.Final):
    def __init__(self, k: K) -> None:
        check.not_in(k.__class__, _KEY_TYPES)
        self._k = k

    def __repr__(self) -> str:
        return f'orm.key({self._k!r})'

    @property
    def k(self) -> K:
        return self._k

    #

    def __hash__(self) -> int:
        return hash(self._k)

    def __eq__(self, other: object) -> bool:
        return other.__class__ is _Key and self._k == other._k  # type: ignore[attr-defined]

    def __lt__(self, other: object) -> bool:
        if (oc := other.__class__) is _Key:
            return self._k < other._k  # type: ignore[attr-defined]
        elif oc is _AutoKey:
            return False
        else:
            raise TypeError(other)


@ta.overload
def key(k: Key[K]) -> Key[K]:
    ...


@ta.overload
def key(k: K) -> Key[K]:
    ...


def key(k):
    if k.__class__ in _KEY_TYPES:
        return k
    return _Key(k)


##


class AutoKeyNotSetError(Exception):
    pass


@ta.final
class _AutoKey(Key[K], lang.Final):
    def __repr__(self) -> str:
        return f'orm.auto_key@{id(self):x}'

    @property
    def k(self) -> K:
        raise AutoKeyNotSetError

    #

    def __lt__(self, other: object) -> bool:
        if (oc := other.__class__) is _Key:
            return True
        elif oc is _AutoKey:
            return id(self) < id(other)
        else:
            raise TypeError(other)


def auto_key() -> Key:
    return _AutoKey()


def is_auto_key(k: ta.Any) -> bool:
    return k.__class__ is _AutoKey


##


def _unwrap_key(k: Key) -> ta.Any:
    if k.__class__ is _AutoKey:
        return k
    return k.k


_KEY_TYPES: tuple[type[Key], ...] = (
    _Key,
    _AutoKey,
)
