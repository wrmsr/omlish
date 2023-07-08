import typing as ta

from .identity import IdentitySet
from .identity import IdentityKeyDict


T = ta.TypeVar('T')


class IndexedSeq(ta.Sequence[T]):

    def __init__(self, it: ta.Iterable[T], *, identity: bool = False) -> None:
        super().__init__()

        self._lst = list(it)
        self._idxs = (IdentityKeyDict if identity else dict)(map(reversed, enumerate(self._lst)))
        if len(self._idxs) != len(self._lst):
            raise ValueError(f'{len(self._idxs)} != {len(self._lst)}')

    @property
    def debug(self) -> ta.Sequence[T]:
        return self._lst

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._lst)

    def __getitem__(self, idx: int) -> T:  # type: ignore
        return self._lst[idx]

    def __len__(self) -> int:
        return len(self._lst)

    def __contains__(self, obj: T) -> bool:  # type: ignore
        return obj in self._idxs

    @property
    def idxs(self) -> ta.Mapping[T, int]:
        return self._idxs

    def idx(self, obj: T) -> int:
        return self._idxs[obj]


class IndexedSetSeq(ta.Sequence[ta.AbstractSet[T]]):

    def __init__(self, it: ta.Iterable[ta.Iterable[T]], *, identity: bool = False) -> None:
        super().__init__()

        self._lst = [(IdentitySet if identity else set)(e) for e in it]
        self._idxs = (IdentityKeyDict if identity else dict)((e, i) for i, es in enumerate(self._lst) for e in es)
        if len(self._idxs) != sum(map(len, self._lst)):
            raise ValueError(f'{len(self._idxs)} != {sum(map(len, self._lst))}')

    @property
    def debug(self) -> ta.Sequence[ta.AbstractSet[T]]:
        return self._lst

    def __iter__(self) -> ta.Iterator[ta.AbstractSet[T]]:
        return iter(self._lst)

    def __getitem__(self, idx: int) -> ta.AbstractSet[T]:  # type: ignore
        return self._lst[idx]

    def __len__(self) -> int:
        return len(self._lst)

    def __contains__(self, obj: T) -> bool:  # type: ignore
        return obj in self._idxs

    @property
    def idxs(self) -> ta.Mapping[T, int]:
        return self._idxs

    def idx(self, obj: T) -> int:
        return self._idxs[obj]
