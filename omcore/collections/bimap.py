"""
TODO:
 - key_dict_factory, value_dict_factory
"""
import abc
import typing as ta

from .. import check
from .. import lang
from .mappings import DictFactory


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class BiMap(ta.Mapping[K, V], lang.Abstract):
    @property
    @abc.abstractmethod
    def inverse(self) -> BiMap[V, K]:
        raise NotImplementedError


#


class _BaseBiMapImpl(BiMap[K, V], lang.Abstract):
    def __init__(
            self,
            dct: ta.Mapping[K, V],
            inverse: BiMap[V, K],
    ) -> None:
        super().__init__()

        self._dct = dct
        self._inverse = inverse

    @property
    def inverse(self) -> BiMap[V, K]:
        return self._inverse

    def __repr__(self) -> str:
        return f'BiMap({self._dct!r})'

    #

    def __getitem__(self, key, /):
        return self._dct[key]

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)


class _BiMapImpl(_BaseBiMapImpl[K, V]):
    def __init__(
            self,
            items: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]],
            *,
            key_factory: DictFactory | None = None,
            value_factory: DictFactory | None = None,
    ) -> None:
        dct: ta.MutableMapping[K, V] = (key_factory or dict)()
        inv_dct: ta.MutableMapping[V, K] = (value_factory or dict)()
        for k, v in lang.yield_dict_init(items):
            check.not_in(k, dct)
            check.not_in(v, inv_dct)
            dct[k] = v
            inv_dct[v] = k

        super().__init__(dct, _BiMapImpl._Inverse(inv_dct, self))

    class _Inverse(_BaseBiMapImpl):
        pass


#


def make_bi_map(
        items: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]] = (),
        *,
        key_factory: DictFactory | None = None,
        value_factory: DictFactory | None = None,
) -> BiMap[K, V]:
    return _BiMapImpl(
        items,
        key_factory=key_factory,
        value_factory=value_factory,
    )


##


class MutableBiMap(ta.MutableMapping[K, V], lang.Abstract):
    @property
    @abc.abstractmethod
    def inverse(self) -> MutableBiMap[V, K]:
        raise NotImplementedError


#


class _BaseMutableBiMapImpl(MutableBiMap[K, V], lang.Abstract):
    _inverse: _BaseMutableBiMapImpl[V, K]

    def __init__(
            self,
            dct: ta.MutableMapping[K, V],
            inverse: _BaseMutableBiMapImpl[V, K],
    ) -> None:
        super().__init__()

        self._dct = dct
        self._inverse = inverse

    @property
    def inverse(self) -> MutableBiMap[V, K]:
        return self._inverse

    def __repr__(self) -> str:
        return f'MutableBiMap({self._dct!r})'

    #

    def __getitem__(self, key, /):
        return self._dct[key]

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)

    def __setitem__(self, key, value, /):
        other = self._inverse._dct  # noqa

        try:
            existing_key = other[value]
        except KeyError:
            pass
        else:
            if existing_key != key:
                raise ValueError(value)

        try:
            old_value = self._dct[key]
        except KeyError:
            pass
        else:
            del other[old_value]

        self._dct[key] = value
        other[value] = key

    def __delitem__(self, key, /):
        value = self._dct[key]
        del self._dct[key]
        del self._inverse._dct[value]  # noqa

    def update(self, other=(), /, **kwargs):
        # Collapse the batch into a plain dict first (last-wins per key, matching dict.update semantics for iterables of
        # pairs).
        new: dict = {}
        if isinstance(other, ta.Mapping):
            new.update(other)
        else:
            for k, v in other:
                new[k] = v  # noqa
        new.update(kwargs)

        if not new:
            return

        # Phase 1: validate against the merged final state. No mutation yet.
        merged = dict(self._dct)
        merged.update(new)

        seen: dict = {}
        for k, v in merged.items():
            if v in seen:
                raise ValueError(v)
            seen[v] = k

        # Phase 2: apply. Validation guarantees every value in `new` is either fresh or owned by a key that is itself
        # reassigned in `new`, so deleting all stale inverse entries before inserting handles swaps and rotations.
        # Nothing below can raise, so the whole batch lands.
        inv_dct = self._inverse._dct  # noqa

        for k in new:
            try:
                old_v = self._dct[k]
            except KeyError:
                pass
            else:
                del inv_dct[old_v]

        for k, v in new.items():
            self._dct[k] = v
            inv_dct[v] = k


class _MutableBiMapImpl(_BaseMutableBiMapImpl[K, V]):
    def __init__(
            self,
            items: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]],
            *,
            key_factory: DictFactory | None = None,
            value_factory: DictFactory | None = None,
    ) -> None:
        dct: ta.MutableMapping[K, V] = (key_factory or dict)()
        inv_dct: ta.MutableMapping[V, K] = (value_factory or dict)()

        super().__init__(dct, _MutableBiMapImpl._Inverse(inv_dct, self))

        self._inv_dct = inv_dct

        for k, v in lang.yield_dict_init(items):
            self[k] = v

    class _Inverse(_BaseMutableBiMapImpl):
        pass


#


def make_mutable_bi_map(
        items: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]] = (),
        *,
        key_factory: DictFactory | None = None,
        value_factory: DictFactory | None = None,
) -> MutableBiMap[K, V]:
    return _MutableBiMapImpl(
        items,
        key_factory=key_factory,
        value_factory=value_factory,
    )
