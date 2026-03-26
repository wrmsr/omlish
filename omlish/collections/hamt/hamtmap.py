import operator
import typing as ta

from ... import check
from ..mappings import IterItemsViewMapping
from ..mappings import IterValuesViewMapping
from ..persistent import PersistentMapping


try:
    from . import _hamt  # type: ignore
except ImportError:
    pass


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


@ta.final
class HamtMap(
    IterValuesViewMapping[K, V],
    IterItemsViewMapping[K, V],
    PersistentMapping[K, V],
):
    def __init__(self, *, _h: ta.Any | None = None) -> None:
        self._h = _h if _h is not None else _hamt.new()

    def __len__(self) -> int:
        return _hamt.len(self._h)

    def __contains__(self, item: K) -> bool:  # type: ignore[override]
        return _hamt.find(self._h, item) is not None

    def __getitem__(self, item: K) -> V:
        if (v := _hamt.find(self._h, item)) is None:
            raise KeyError(item)
        return v

    def __iter__(self) -> ta.Iterator[K]:
        return _hamt.iter_keys(self._h)

    def iteritems(self) -> ta.Iterator[tuple[K, V]]:
        return _hamt.iter_items(self._h)

    def itervalues(self) -> ta.Iterator[V]:
        return map(operator.itemgetter(1), self.iteritems())

    def with_(self, k: K, v: V) -> ta.Self:
        return HamtMap(_h=_hamt.assoc(self._h, k, check.not_none(v)))

    def without(self, k: K) -> ta.Self:
        if (h2 := _hamt.without(h1 := self._h, k)) is h1:
            return self
        return HamtMap(_h=h2)

    def default(self, k: K, v: V) -> ta.Self:
        if _hamt.find(self._h, k) is not None:
            return self
        return self.with_(k, v)


def new_hamt_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
) -> HamtMap[K, V]:
    m: HamtMap[K, V] = HamtMap()
    if items is not None:
        for k, v in items:
            m = m.with_(k, v)
    return m


def is_hamt_available() -> bool:
    try:
        _hamt  # noqa
    except NameError:
        return False
    else:
        return True
