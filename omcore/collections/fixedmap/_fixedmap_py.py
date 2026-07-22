import sys
import types
import typing as ta

from ... import lang
from ..mappings import IterItemsViewMapping
from ..mappings import IterValuesViewMapping
from .fixedmap import FixedMap as BaseFixedMap
from .fixedmap import FixedMapKeys as BaseFixedMapKeys


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


_UHASH_MASK = 2 * sys.maxsize + 1  # (Py_uhash_t)-1


def _hash_items(items: ta.Iterable[ta.Any]) -> int:
    # Order-insensitive hash, frozenset's entry mixing over hash((key, value)) pairs: mapping equality (both against
    # other FixedMaps and against dicts) is content-based and ignores key order, so the hash must be too. MUST stay
    # bit-identical to FixedMap_hash in _fixedmap.cc -- equal maps must hash equal across the two implementations,
    # which coexist in-process.
    h = 0
    n = 0

    for it in items:
        eh = hash(it) & _UHASH_MASK
        h ^= ((eh ^ 89869747) ^ ((eh << 16) & _UHASH_MASK)) * 3644798167 & _UHASH_MASK
        n += 1

    h ^= ((n + 1) * 1927868237) & _UHASH_MASK
    h ^= (h >> 11) ^ (h >> 25)
    h = (h * 69069 + 907133923) & _UHASH_MASK

    if h in (_UHASH_MASK, 0):
        # -1 is reserved by CPython; 0 is the C implementation's "uncomputed" cache sentinel.
        h = 590923713

    if h > sys.maxsize:
        h -= _UHASH_MASK + 1

    return h


@ta.final
class FixedMapKeys(
    BaseFixedMapKeys[K],
    ta.Generic[K],
):
    __slots__ = ('_keys', '_key_indexes')

    def __init__(self, keys: ta.Iterable[K]) -> None:
        self._keys = keys = tuple(keys)
        key_indexes: dict[K, int] = {}
        for k in keys:
            if k in key_indexes:
                raise lang.DuplicateKeyError(k)
            key_indexes[k] = len(key_indexes)
        self._key_indexes = key_indexes

    @property
    def fixed_keys(self) -> tuple[K, ...]:
        return self._keys

    #

    @property
    def debug(self) -> ta.Mapping[K, int]:
        return types.MappingProxyType(self._key_indexes)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._key_indexes!r})'

    #

    def __hash__(self) -> int:
        return hash(self._keys)

    def __getitem__(self, key: K, /) -> int:
        return self._key_indexes[key]

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self._keys)

    #

    def keys(self) -> ta.KeysView[K]:
        return self._key_indexes.keys()

    def values(self) -> ta.ValuesView[int]:
        return self._key_indexes.values()

    def items(self) -> ta.ItemsView[K, int]:
        return self._key_indexes.items()


@ta.final
class FixedMap(
    IterValuesViewMapping[K, V],
    IterItemsViewMapping[K, V],
    BaseFixedMap[K, V],
    ta.Mapping[K, V],
    ta.Generic[K, V],
):
    __slots__ = ('_keys', '_values', '_hash')

    def __init__(self, keys: FixedMapKeys[K], values: ta.Sequence[V]) -> None:
        self._keys, self._values = keys, tuple(values)

    @property
    def fixed_keys(self) -> FixedMapKeys[K]:
        return self._keys

    @property
    def fixed_values(self) -> tuple[V, ...]:
        return self._values

    #

    @property
    def debug(self) -> ta.Mapping[K, V]:
        return {k: self._values[i] for k, i in self._keys.items()}

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.debug!r})'

    #

    _hash: int

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass
        self._hash = h = _hash_items(zip(self._keys, self._values, strict=True))
        return h

    #

    def __getitem__(self, key: K, /) -> V:
        return self._values[self._keys[key]]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self._keys)

    #

    def itervalues(self) -> ta.Iterator[V]:
        return iter(self._values)

    def iteritems(self) -> ta.Iterator[tuple[K, V]]:
        return iter(zip(self._keys, self._values, strict=True))
