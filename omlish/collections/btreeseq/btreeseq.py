"""Persistent counted B+-ish sequence with dense leaves and opportunistic compaction."""
import operator
import typing as ta

from ..iterators import HasNextIterator
from ..persistent import PersistentSequence
from . import _btreeseq_py as _backend


try:
    from . import _btreeseq  # type: ignore
except ImportError:
    pass
else:
    _backend = _btreeseq  # noqa


T = ta.TypeVar('T')


##


class BtreeSeq(
    PersistentSequence[T],
    ta.Sequence[T],
    ta.Generic[T],
):
    __slots__ = ('_root',)

    _backend: ta.Final = _backend

    def __init__(
            self,
            *,
            _root: ta.Any,
    ) -> None:
        super().__init__()

        self._root = _root

    @property
    def debug(self) -> tuple[T, ...]:
        return tuple(self)

    def __len__(self) -> int:
        return self._backend.len_(self._root)

    @ta.overload
    def __getitem__(self, item: int) -> T:
        ...

    @ta.overload
    def __getitem__(self, item: slice) -> ta.Self:
        ...

    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop = self._normalize_slice(item)
            root = self._backend.slice(self._root, start, stop)

            if root is self._root:
                return self

            return self.__class__(_root=root)

        idx = self._normalize_index(item)
        return self._backend.get(self._root, idx)

    def __reversed__(self) -> HasNextIterator[T]:
        return self._backend.riter(self._root)

    def iter_from(self, idx: int) -> HasNextIterator[T]:
        start, _ = self._normalize_bounds(idx, None)
        return self._backend.iter_from(self._root, start)

    def index(self, value: ta.Any, start: int = 0, stop: int | None = None) -> int:
        start, stop = self._normalize_bounds(start, stop)
        it = self._backend.iter_from(self._root, start)

        for i in range(start, stop):
            if (v := next(it)) is value or v == value:
                return i

        raise ValueError(value)

    def __iter__(self) -> HasNextIterator[T]:
        return self._backend.iter(self._root)

    def splice(
            self,
            start: int | None,
            stop: int | None,
            items: ta.Iterable[T],
    ) -> ta.Self:
        start, stop = self._normalize_bounds(start, stop)

        root = self._backend.splice(self._root, start, stop, items)

        if root is self._root:
            return self

        return self.__class__(_root=root)

    def with_(self, idx: int, item: T) -> ta.Self:
        idx = self._normalize_index(idx)

        return self.splice(idx, idx + 1, (item,))

    def without(self, item: int | slice) -> ta.Self:
        if isinstance(item, slice):
            start, stop = self._normalize_slice(item)
            return self.splice(start, stop, ())

        idx = self._normalize_index(item)
        return self.splice(idx, idx + 1, ())

    def append(self, item: T) -> ta.Self:
        return self.splice(len(self), len(self), (item,))

    def extend(self, items: ta.Iterable[T]) -> ta.Self:
        ln = len(self)

        return self.splice(ln, ln, items)

    def _normalize_index(self, idx: int) -> int:
        idx = operator.index(idx)

        ln = len(self)

        if idx < 0:
            idx += ln

        if idx < 0 or idx >= ln:
            raise IndexError(idx)

        return idx

    def _normalize_slice(self, slc: slice) -> tuple[int, int]:
        if slc.step not in (None, 1):
            raise ValueError('slice steps other than 1 are not supported')

        start, stop, _ = slc.indices(len(self))

        if stop < start:
            stop = start

        return start, stop

    def _normalize_bounds(
            self,
            start: int | None,
            stop: int | None,
    ) -> tuple[int, int]:
        start, stop, _ = slice(start, stop).indices(len(self))

        if stop < start:
            stop = start

        return start, stop


def new_btree_seq(items: ta.Iterable[T] | None = None) -> BtreeSeq[T]:
    return BtreeSeq(
        _root=_backend.from_iterable(()) if items is None else _backend.from_iterable(items),
    )
