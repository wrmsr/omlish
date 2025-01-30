import dataclasses as dc
import typing as ta

from .... import collections as col


##


@dc.dataclass(frozen=True)
class NumericReply:
    name: str
    num: int
    formats: ta.Sequence[str]

    @classmethod
    def new(
            cls,
            name: str,
            num: int,
            *formats: str,
    ) -> 'NumericReply':
        return cls(
            name,
            num,
            formats,
        )


##


class NumericReplies:
    def __init__(self, lst: ta.Iterable[NumericReply]) -> None:
        super().__init__()

        self._lst = list(lst)
        self._by_name = col.make_map_by(lambda nr: nr.name, self._lst, strict=True)
        self._by_num = col.make_map_by(lambda nr: nr.num, self._lst, strict=True)

    def __len__(self) -> int:
        return len(self._lst)

    def __iter__(self) -> ta.Iterator[NumericReply]:
        return iter(self._lst)

    def __getitem__(self, key: str | int) -> NumericReply:
        if isinstance(key, str):
            return self._by_name[key]
        elif isinstance(key, int):
            return self._by_num[key]
        else:
            raise TypeError(key)

    def get(self, key: str | int) -> NumericReply | None:
        try:
            return self[key]
        except KeyError:
            return None
