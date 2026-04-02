import typing as ta

from .mappings import IterItemsViewMapping
from .mappings import IterValuesViewMapping


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


@ta.final
class FixedMapping(
    IterValuesViewMapping,
    IterItemsViewMapping,
    ta.Mapping[K, V],
):
    """
    Required invariants:
     - `len(keys) must == len(values)
     - `keys` indexes must be a densely packed 0-based range

    These are invariants are not eagerly checked.
    """

    def __init__(self, keys: ta.Mapping[K, int], values: ta.Sequence[V]) -> None:
        self._keys, self._values = keys, values

    def _check_invariants(self) -> None:
        if len(self._keys) != len(self._values):
            raise ValueError(f'len(keys) != len(values): {len(self._keys)} != {len(self._values)}')
        if set(self._keys.values()) != set(range(len(self._keys))):
            raise ValueError('key indexes must be a densely packed 0-based range')

    @property
    def fixed_keys(self) -> ta.Mapping[K, int]:
        return self._keys

    @property
    def fixed_values(self) -> ta.Sequence[V]:
        return self._values

    #

    @property
    def debug(self) -> dict[K, V]:
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
        self._hash = h = hash(tuple(zip(self._keys, self._values, strict=True)))
        return h

    #

    def __getitem__(self, key: K, /) -> V:
        return self._values[self._keys[key]]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self._keys)

    def itervalues(self) -> ta.Iterator[V]:
        return iter(self._values)

    def iteritems(self) -> ta.Iterator[tuple[K, V]]:
        return iter(zip(self._keys, self._values, strict=True))
