import abc
import typing as ta

from ... import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class FixedMapKeys(
    ta.Mapping[K, int],
    lang.Abstract,
    ta.Generic[K],
):
    @property
    @abc.abstractmethod
    def fixed_keys(self) -> tuple[K, ...]:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def debug(self) -> ta.Mapping[K, int]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError


class FixedMap(
    ta.Mapping[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    @property
    @abc.abstractmethod
    def fixed_keys(self) -> FixedMapKeys[K]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def fixed_values(self) -> tuple[V, ...]:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def debug(self) -> ta.Mapping[K, V]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def itervalues(self) -> ta.Iterator[V]:
        raise NotImplementedError

    @abc.abstractmethod
    def iteritems(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError


##


try:
    from . import _fixedmap as _impl  # type: ignore
except ImportError:
    from . import _fixedmap_py as _impl


def new_fixed_map(src: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]]) -> FixedMap[K, V]:
    if isinstance(src, ta.Mapping):
        src = src.items()
    keys: list[K] = []
    values: list[V] = []
    for k, v in src:
        keys.append(k)
        values.append(v)
    return _impl.FixedMap(_impl.FixedMapKeys(keys), values)
