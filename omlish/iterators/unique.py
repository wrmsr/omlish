import dataclasses as dc
import typing as ta

from .. import lang


T = ta.TypeVar('T')


@dc.dataclass()
class UniqueStats:
    key: ta.Any
    num_seen: int
    first_idx: int
    last_idx: int


@dc.dataclass(frozen=True)
class UniqueItem(ta.Generic[T]):
    idx: int
    item: T
    stats: UniqueStats
    out: lang.Maybe[T]


class UniqueIterator(ta.Iterator[UniqueItem[T]]):
    def __init__(
            self,
            it: ta.Iterable[T],
            keyer: ta.Callable[[T], ta.Any] = lang.identity,
    ) -> None:
        super().__init__()
        self._it = enumerate(it)
        self._keyer = keyer

        self.stats: dict[ta.Any, UniqueStats] = {}

    def __next__(self) -> UniqueItem[T]:
        idx, item = next(self._it)
        key = self._keyer(item)

        try:
            stats = self.stats[key]

        except KeyError:
            stats = self.stats[key] = UniqueStats(
                key,
                num_seen=1,
                first_idx=idx,
                last_idx=idx,
            )
            return UniqueItem(
                idx,
                item,
                stats,
                lang.just(item),
            )

        else:
            stats.num_seen += 1
            stats.last_idx = idx
            return UniqueItem(
                idx,
                item,
                stats,
                lang.empty(),
            )
