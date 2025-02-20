import dataclasses as dc
import typing as ta

from ... import lang
from .errors import DuplicateColumnNameError


##


@dc.dataclass(frozen=True)
class Column(lang.Final):
    name: str

    _: dc.KW_ONLY

    db_type: str | None = None
    type: type = object


##


class Columns(lang.Final):
    def __init__(self, *cs: Column) -> None:
        super().__init__()

        self._seq = cs

        by_name: dict[str, Column] = {}
        idxs_by_name: dict[str, int] = {}
        for i, c in enumerate(cs):
            if c.name in by_name:
                raise DuplicateColumnNameError(c.name)
            by_name[c.name] = c
            idxs_by_name[c.name] = i

        self._by_name = by_name
        self._idxs_by_name = idxs_by_name

    #

    _EMPTY: ta.ClassVar['Columns']

    @classmethod
    def empty(cls) -> 'Columns':
        return cls._EMPTY

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{", ".join(repr(c.name) for c in self._seq)}>'

    #

    def __iter__(self) -> ta.Iterator[Column]:
        return iter(self._seq)

    def __len__(self) -> int:
        return len(self._seq)

    def __contains__(self, item: str | int) -> bool:
        if isinstance(item, str):
            return item in self._by_name
        elif isinstance(item, int):
            return 0 <= item < len(self._by_name)
        else:
            raise TypeError(item)

    def __getitem__(self, item) -> Column:
        if isinstance(item, str):
            return self._by_name[item]
        elif isinstance(item, int):
            return self._seq[item]
        else:
            raise TypeError(item)

    def get(self, name: str) -> Column | None:
        return self._by_name.get(name)

    #

    def index(self, name: str) -> int:
        return self._idxs_by_name[name]

    def get_index(self, name: str) -> int | None:
        return self._idxs_by_name.get(name)


Columns._EMPTY = Columns()  # noqa
