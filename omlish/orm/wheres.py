import enum
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


if ta.TYPE_CHECKING:
    from . import wrappers as _wrappers
else:
    _wrappers = lang.proxy_import('.wrappers', __package__)


##


class WhereOp(enum.Enum):
    EQ = '='
    NE = '!='
    LT = '<'
    LE = '<='
    GE = '>='
    GT = '>'


@ta.final
@dc.dataclass(frozen=True)
class WhereItem(lang.Final):
    field: str
    op: WhereOp
    value: ta.Any

    def __post_init__(self) -> None:
        check.not_isinstance(self.value, _wrappers.WRAPPER_TYPES)


@ta.final
class Wheres(ta.Sequence[WhereItem], lang.Final):
    def __init__(
            self,
            items: ta.Sequence[WhereItem],
    ) -> None:
        super().__init__()

        self._items = items
        self._items_by_field: dict[str, WhereItem] = {}
        for item in self._items:
            check.not_in(item.field, self._items_by_field)
            self._items_by_field[item.field] = item

    def __iter__(self) -> ta.Iterator[WhereItem]:
        return iter(self._items)

    @ta.overload
    def __getitem__(self, index: int | str) -> WhereItem: ...

    @ta.overload
    def __getitem__(self, index: slice) -> ta.Sequence[WhereItem]: ...

    def __getitem__(self, index):
        if isinstance(index, str):
            return self._items_by_field[index]
        else:
            return self._items[index]

    def __len__(self) -> int:
        return len(self._items)


_WHERES_TYPES: tuple[type, ...] = (
    WhereItem,
    Wheres,
)
