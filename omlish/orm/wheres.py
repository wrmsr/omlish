import enum
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


##


class WhereOp(enum.Enum):
    EQ = '='
    NE = '!='
    LT = '<'
    LE = '<='
    GE = '>='
    GT = '>'


WhereOpGlyph: ta.TypeAlias = ta.Literal[
    '=',
    '!=',
    '<',
    '<=',
    '>=',
    '>',
]


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class WhereItem(lang.Final):
    field: str
    op: WhereOp
    value: ta.Any

    # Note: can't - needs to take refs and stuff.
    # def __post_init__(self) -> None:
    #     check.not_in(self.value.__class__, _wrappers.WRAPPER_TYPES)


@ta.final
class Where(ta.Sequence[WhereItem], lang.Final):
    def __init__(
            self,
            *items: WhereItem,
    ) -> None:
        super().__init__()

        self._items = items
        self._by_field: dict[str, WhereItem] = {}
        is_all_eq = True
        for item in self._items:
            check.not_in(item.field, self._by_field)
            if item.op is not WhereOp.EQ:
                is_all_eq = False
            self._by_field[item.field] = item
        self._is_all_eq = is_all_eq

    @classmethod
    def of_eq(cls, **field_values: ta.Any) -> Where:
        return cls(*(
            WhereItem(k, WhereOp.EQ, v)
            for k, v in field_values.items()
        ))

    def __repr__(self) -> str:
        return ''.join([
            f'{self.__class__.__name__}(',
            ', '.join([repr(i) for i in self._items]),
            ')',
        ])

    @property
    def by_field(self) -> ta.Mapping[str, WhereItem]:
        return self._by_field

    @property
    def is_all_eq(self) -> bool:
        return self._is_all_eq

    def eq_dict(self) -> dict[str, ta.Any]:
        check.state(self.is_all_eq)
        return {i.field: i.value for i in self._items}

    def __bool__(self) -> bool:
        return bool(self._items)

    def __iter__(self) -> ta.Iterator[WhereItem]:
        return iter(self._items)

    @ta.overload
    def __getitem__(self, index: int | str) -> WhereItem: ...

    @ta.overload
    def __getitem__(self, index: slice) -> ta.Sequence[WhereItem]: ...

    def __getitem__(self, index):
        if isinstance(index, str):
            return self._by_field[index]
        else:
            return self._items[index]

    def __len__(self) -> int:
        return len(self._items)


_WHERES_TYPES: tuple[type, ...] = (
    WhereItem,
    Where,
)
