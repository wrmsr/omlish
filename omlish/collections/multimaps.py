import abc
import typing as ta

from .. import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')
MV = ta.TypeVar('MV', bound=ta.Iterable)


##


class MultiMap(ta.Mapping[K, MV], abc.ABC, ta.Generic[K, V, MV]):
    """Explicitly an abc.ABC, not a lang.Abstract, to support virtual subclassing."""


SequenceMultiMap: ta.TypeAlias = MultiMap[K, V, ta.Sequence[V]]
AbstractSetMultiMap: ta.TypeAlias = MultiMap[K, V, ta.AbstractSet[V]]


##


class BiMultiMap(MultiMap[K, V, MV], abc.ABC, ta.Generic[K, V, MV]):
    @abc.abstractmethod
    def inverse(self) -> 'InverseBiMultiMap[K, V, MV]':
        raise NotImplementedError


class InverseBiMultiMap(ta.Mapping[V, K], abc.ABC, ta.Generic[K, V, MV]):
    @abc.abstractmethod
    def inverse(self) -> BiMultiMap[K, V, MV]:
        raise NotImplementedError


SequenceBiMultiMap: ta.TypeAlias = BiMultiMap[K, V, ta.Sequence[V]]
AbstractSetBiMultiMap: ta.TypeAlias = BiMultiMap[K, V, ta.AbstractSet[V]]


##


class InverseBiMultiMapImpl(InverseBiMultiMap[K, V, MV], ta.Generic[K, V, MV]):
    def __init__(self, m: BiMultiMap[K, V, MV], dct: ta.Mapping[V, K]) -> None:
        super().__init__()

        self._m = m
        self._dct = dct

    def inverse(self) -> BiMultiMap[K, V, MV]:
        return self._m

    def __getitem__(self, key: V, /) -> K:
        return self._dct[key]

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[V]:
        return iter(self._dct)


class BaseBiMultiMap(BiMultiMap[K, V, MV], abc.ABC, ta.Generic[K, V, MV]):
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()

        dct: dict[K, MV] = {}
        i_dct: dict[V, K] = {}
        for k, mv in lang.yield_dict_init(*args, **kwargs):
            l: list[V] = []
            for v in mv:
                if v in i_dct:
                    raise KeyError(v)
                l.append(v)
                i_dct[v] = k
            dct[k] = self._aggregate_values(l)

        self._dct = dct
        self._i: InverseBiMultiMap[K, V, MV] = InverseBiMultiMapImpl(self, i_dct)

    @abc.abstractmethod
    def _aggregate_values(self, vs: list[V]) -> MV:
        raise NotImplementedError

    def inverse(self) -> 'InverseBiMultiMap[K, V, MV]':
        return self._i

    def __getitem__(self, key: K, /) -> MV:
        return self._dct[key]

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self._dct)


#


class TupleBiMultiMap(BaseBiMultiMap[K, V, tuple[V, ...]], ta.Generic[K, V]):
    def _aggregate_values(self, vs: list[V]) -> tuple[V, ...]:
        return tuple(vs)


# FIXME: lame
# lang.static_check_issubclass[BiMultiMap[int, str, tuple[str, ...]]](TupleBiMultiMap[int, str])
# lang.static_check_issubclass[BiMultiMap[int, str, ta.Sequence[str]]](TupleBiMultiMap[int, str])
# lang.static_check_issubclass[SequenceBiMultiMap[int, str]](TupleBiMultiMap[int, str])


@ta.overload
def seq_bi_multi_map(dct: ta.Mapping[K, ta.Iterable[V]]) -> SequenceBiMultiMap[K, V]:
    ...


@ta.overload
def seq_bi_multi_map(items: ta.Iterable[tuple[K, ta.Iterable[V]]]) -> SequenceBiMultiMap[K, V]:
    ...


def seq_bi_multi_map(*args, **kwargs):
    return TupleBiMultiMap(*args, **kwargs)


#


class FrozensetBiMultiMap(BaseBiMultiMap[K, V, frozenset[V]], ta.Generic[K, V]):
    def _aggregate_values(self, vs: list[V]) -> frozenset[V]:
        return frozenset(vs)


# FIXME: lame
# lang.static_check_issubclass[AbstractSetBiMultiMap[int, str]](FrozensetBiMultiMap[int, str])


@ta.overload
def abs_set_bi_multi_map(dct: ta.Mapping[K, ta.Iterable[V]]) -> AbstractSetBiMultiMap[K, V]:
    ...


@ta.overload
def abs_set_bi_multi_map(items: ta.Iterable[tuple[K, ta.Iterable[V]]]) -> AbstractSetBiMultiMap[K, V]:
    ...


def abs_set_bi_multi_map(*args, **kwargs):
    return FrozensetBiMultiMap(*args, **kwargs)
