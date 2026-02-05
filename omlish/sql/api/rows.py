import typing as ta

from ... import dataclasses as dc
from ... import lang
from .columns import Column
from .columns import Columns
from .errors import MismatchedColumnCountError


T = ta.TypeVar('T')


##


@ta.final
class ColumnAccessor(lang.Final, ta.Generic[T]):
    def __init__(self, row: 'Row') -> None:
        self.__row = row

    def __getattr__(self, name: str) -> T:
        return self.__row[name]


@dc.dataclass(frozen=True)
class Row(lang.Final, ta.Generic[T]):
    columns: Columns
    values: ta.Sequence[T]

    def __post_init__(self) -> None:
        if len(self.columns) != len(self.values):
            raise MismatchedColumnCountError(self.columns, self.values)

    #

    def __iter__(self) -> ta.Iterator[tuple[Column, T]]:
        return iter(zip(self.columns, self.values))

    def __len__(self) -> int:
        return len(self.values)

    def __contains__(self, item: str | int) -> bool:
        raise TypeError('Row.__contains__ is ambiguous - use .columns.__contains__ or .values.__contains__')

    def __getitem__(self, item: str | int) -> T:
        if isinstance(item, str):
            return self.values[self.columns.index(item)]
        elif isinstance(item, int):
            return self.values[item]
        else:
            raise TypeError(item)

    def get(self, name: str) -> T | None:
        if (idx := self.columns.get_index(name)) is not None:
            return self.values[idx]
        else:
            return None

    @property
    def c(self) -> ColumnAccessor[T]:
        return ColumnAccessor(self)

    def to_dict(self) -> dict[str, ta.Any]:
        return {c.name: v for c, v in self}
