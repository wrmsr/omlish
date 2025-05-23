import abc
import typing as ta

from .. import check
from .. import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')

K2 = ta.TypeVar('K2')
V2 = ta.TypeVar('V2')


##


class BiMap(ta.Mapping[K, V], lang.Abstract):
    @abc.abstractmethod
    def inverse(self) -> 'BiMap[V, K]':
        raise NotImplementedError


##


class _BaseBiMapImpl(BiMap[K, V], lang.Abstract):
    def __init__(
            self,
            dct: ta.Mapping[K, V],
            inverse: BiMap[V, K],
    ) -> None:
        super().__init__()

        self._dct = dct
        self._inverse = inverse

    def inverse(self) -> 'BiMap[V, K]':
        return self._inverse

    def __getitem__(self, key, /):
        return self._dct[key]

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)


class _BiMapImpl(_BaseBiMapImpl[K, V]):
    def __init__(self, *args, **kwargs) -> None:
        dct: dict[K, V] = {}
        inv_dct: dict[V, K] = {}
        for k, v in lang.yield_dict_init(*args, **kwargs):
            check.not_in(k, dct)
            check.not_in(v, dct)
            dct[k] = v
            inv_dct[v] = k

        self._dct = dct
        self._inv_dct = inv_dct

        super().__init__(dct, _BiMapImpl._Inverse(inv_dct, self))

    class _Inverse(_BaseBiMapImpl):
        pass


##


@ta.overload
def make_bi_map(dct: ta.Mapping[K, V]) -> BiMap[K, V]:
    ...


@ta.overload
def make_bi_map(items: ta.Iterable[tuple[K, V]]) -> BiMap[K, V]:
    ...


@ta.overload
def make_bi_map(**kwargs: str) -> BiMap[str, str]:
    ...


def make_bi_map(*args, **kwargs):
    return _BiMapImpl(*args, **kwargs)
