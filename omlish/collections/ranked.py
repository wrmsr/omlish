import typing as ta

from .identity import IdentityKeyDict
from .identity import IdentitySet


T = ta.TypeVar('T')


##


class RankedSeq(ta.Sequence[T]):
    def __init__(self, it: ta.Iterable[T], *, identity: bool = False) -> None:
        super().__init__()

        self._lst = list(it)
        self._ranks: ta.Mapping[T, int] = (IdentityKeyDict if identity else dict)((e, i) for i, e in enumerate(self._lst))  # noqa
        if len(self._ranks) != len(self._lst):
            raise ValueError(f'{len(self._ranks)} != {len(self._lst)}')

    @property
    def debug(self) -> ta.Sequence[T]:
        return self._lst

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._lst)

    def __getitem__(self, rank: int) -> T:  # type: ignore
        return self._lst[rank]

    def __len__(self) -> int:
        return len(self._lst)

    def __contains__(self, obj: T) -> bool:  # type: ignore
        return obj in self._ranks

    @property
    def ranks(self) -> ta.Mapping[T, int]:
        return self._ranks

    def rank(self, obj: T) -> int:
        return self._ranks[obj]


##


class RankedSetSeq(ta.Sequence[ta.AbstractSet[T]]):
    def __init__(self, it: ta.Iterable[ta.Iterable[T]], *, identity: bool = False) -> None:
        super().__init__()

        self._lst = [(IdentitySet if identity else set)(e) for e in it]
        self._ranks: ta.Mapping[T, int] = (IdentityKeyDict if identity else dict)((e, i) for i, es in enumerate(self._lst) for e in es)  # noqa
        if len(self._ranks) != sum(map(len, self._lst)):
            raise ValueError(f'{len(self._ranks)} != {sum(map(len, self._lst))}')

    @property
    def debug(self) -> ta.Sequence[ta.AbstractSet[T]]:
        return self._lst

    def __iter__(self) -> ta.Iterator[ta.AbstractSet[T]]:
        return iter(self._lst)

    def __getitem__(self, rank: int) -> ta.AbstractSet[T]:  # type: ignore
        return self._lst[rank]

    def __len__(self) -> int:
        return len(self._lst)

    def __contains__(self, obj: T) -> bool:  # type: ignore
        return obj in self._ranks

    @property
    def ranks(self) -> ta.Mapping[T, int]:
        return self._ranks

    def rank(self, obj: T) -> int:
        return self._ranks[obj]
