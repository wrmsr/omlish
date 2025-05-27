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

    def __repr__(self) -> str:
        return f'BiMap({self._dct!r})'


class _BiMapImpl(_BaseBiMapImpl[K, V]):
    def __init__(self, *args, **kwargs) -> None:
        dct: dict[K, V] = {}
        inv_dct: dict[V, K] = {}
        for k, v in lang.yield_dict_init(*args, **kwargs):
            check.not_in(k, dct)
            check.not_in(v, inv_dct)
            dct[k] = v
            inv_dct[v] = k

        super().__init__(dct, _BiMapImpl._Inverse(inv_dct, self))

    class _Inverse(_BaseBiMapImpl):
        pass


##


@ta.overload
def make_bi_map(**kwargs: V) -> BiMap[V, str]:
    ...


@ta.overload
def make_bi_map(dct: ta.Mapping[K, V]) -> BiMap[K, V]:
    ...


@ta.overload
def make_bi_map(items: ta.Iterable[tuple[K, V]]) -> BiMap[K, V]:
    ...


def make_bi_map(*args, **kwargs):
    return _BiMapImpl(*args, **kwargs)
