import typing as ta

from .bases import IterableSizedQueryableKv
from .bases import MutableIterableSizedQueryableKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')


MappingKvBase: ta.TypeAlias = IterableSizedQueryableKv[K, V]
MutableMappingKvBase: ta.TypeAlias = MutableIterableSizedQueryableKv[K, V]


##


class MappingKv(MappingKvBase[K, V]):
    def __init__(self, m: ta.Mapping[K, V]) -> None:
        super().__init__()

        self._m = m

    def __getitem__(self, k: K, /) -> V:
        return self._m[k]

    def __len__(self) -> int:
        return len(self._m)

    def items(self) -> ta.Iterator[tuple[K, V]]:
        return iter(self._m.items())


class MutableMappingKv(MappingKv[K, V], MutableMappingKvBase[K, V]):
    def __init__(self, m: ta.MutableMapping[K, V]) -> None:
        super().__init__(m)

    _m: ta.MutableMapping[K, V]

    def __setitem__(self, k: K, v: V, /) -> None:
        self._m[k] = v

    def __delitem__(self, k: K, /) -> None:
        del self._m[k]


##


class KvMapping(ta.Mapping[K, V]):
    def __init__(self, kv: MappingKvBase[K, V]) -> None:
        super().__init__()

        self._kv = kv

    def __getitem__(self, key: K, /) -> V:
        return self._kv[key]

    def __len__(self) -> int:
        return len(self._kv)

    # FIXME: ItemsView
    def items(self) -> ta.Iterator[tuple[K, V]]:  # type: ignore[override]
        return iter(self._kv.items())

    def __iter__(self) -> ta.Iterator[K]:
        return (k for k, v in self.items())


class KvMutableMapping(KvMapping[K, V], MutableMappingKvBase[K, V], ta.MutableMapping[K, V]):
    def __init__(self, kv: MutableMappingKvBase[K, V]) -> None:
        super().__init__(kv)

    _kv: MutableMappingKvBase[K, V]

    def __setitem__(self, key: K, value: V, /) -> None:
        self._kv[key] = value

    def __delitem__(self, key: K, /) -> None:
        del self._kv[key]
