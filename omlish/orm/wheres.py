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

    @classmethod
    def of(
            cls,
            field: str,
            op: WhereOp | WhereOpGlyph,
            value: ta.Any,
    ) -> WhereItem:
        return cls(
            field,
            WhereOp(op),
            value,
        )


@ta.final
class Where(ta.Sequence[WhereItem], lang.Final):
    def __init__(
            self,
            *items: WhereItem,
    ) -> None:
        super().__init__()

        self._items = items
        by_field: dict[str, list[WhereItem]] = {}
        eq_values: dict[str, ta.Any] = {}
        is_all_eq = True
        for item in self._items:
            check.not_in(item.field, by_field)
            try:
                lst = by_field[item.field]
            except KeyError:
                by_field[item.field] = [item]
            else:
                lst.append(item)
            if item.op is WhereOp.EQ:
                try:
                    xeq = eq_values[item.field]
                except KeyError:
                    eq_values[item.field] = item.value
                else:
                    # FIXME: not, like, illegal lol, just no results
                    check.equal(xeq, item.value)
            else:
                is_all_eq = False
        self._by_field = by_field
        self._eq_values = eq_values
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
    def by_field(self) -> ta.Mapping[str, ta.Sequence[WhereItem]]:
        return self._by_field

    @property
    def is_all_eq(self) -> bool:
        return self._is_all_eq

    @property
    def eqs(self) -> ta.Mapping[str, ta.Any]:
        return self._eq_values

    def __bool__(self) -> bool:
        return bool(self._items)

    def __iter__(self) -> ta.Iterator[WhereItem]:
        return iter(self._items)

    @ta.overload
    def __getitem__(self, index: int) -> WhereItem: ...

    @ta.overload
    def __getitem__(self, index: slice | str) -> ta.Sequence[WhereItem]: ...

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
