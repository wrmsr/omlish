import abc
import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')
MV = ta.TypeVar('MV', bound=ta.Iterable)


##


class MultiMap(ta.Mapping[K, MV], abc.ABC, ta.Generic[K, V, MV]):
    pass


class ListMultiMap(MultiMap[K, V, list[V]], abc.ABC, ta.Generic[K, V]):
    pass


##


class BiMap(ta.Mapping[K, V]):
    @abc.abstractmethod
    def inverse(self) -> 'BiMap[V, K]':
        raise NotImplementedError


##


class BiMultiMap(MultiMap[K, V, MV], abc.ABC, ta.Generic[K, V, MV]):
    @abc.abstractmethod
    def inverse(self) -> 'InverseBiMultiMap[K, V, MV]':
        raise NotImplementedError


class InverseBiMultiMap(ta.Mapping[V, K], abc.ABC, ta.Generic[K, V, MV]):
    @abc.abstractmethod
    def inverse(self) -> BiMultiMap[K, V, MV]:
        raise NotImplementedError


##


class InverseBiMultiMapImpl(InverseBiMultiMap[K, V, MV], ta.Generic[K, V, MV]):
    def __init__(self, m: BiMultiMap[K, V, MV], dct: ta.Mapping[V, K]) -> None:
        super().__init__()

        self._m = m
        self._dct = dct

    def inverse(self) -> BiMultiMap[K, V, MV]:
        return self._m

    def __getitem__(self, key, /):
        return self._dct[key]

    def __len__(self):
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)


class ListBiMultiMap(BiMultiMap[K, V, list[V]], ta.Generic[K, V]):
    def __init__(self, dct: ta.Mapping[K, list[V]]) -> None:
        super().__init__()

        self._dct = dct

        i_dct: dict[V, K] = {}
        for k, mv in self._dct.items():
            for v in mv:
                if v in i_dct:
                    raise KeyError(v)
                i_dct[v] = k

        self._i: InverseBiMultiMap[K, V, list[V]] = InverseBiMultiMapImpl(self, i_dct)

    def inverse(self) -> 'InverseBiMultiMap[K, V, list[V]]':
        return self._i

    def __getitem__(self, key, /):
        return self._dct[key]

    def __len__(self):
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)


def _main() -> None:
    m = ListBiMultiMap({
        'a': [1, 2],
        'b': [3, 4],
        'c': [5],
    })

    print(m['b'])
    print(m.inverse()[2])
    print(m.inverse().inverse()['b'])


if __name__ == '__main__':
    _main()
