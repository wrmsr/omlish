"""
TODO:
 - QualifiedName
 - datatypes
"""
import dataclasses as dc
import typing as ta

from omlish import collections as col
from omlish import lang


#


@dc.dataclass(frozen=True)
class Datatype(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Integer(Datatype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class String(Datatype, lang.Singleton):
    pass


@dc.dataclass(frozen=True)
class Timestamp(Datatype, lang.Singleton):
    pass


#


class Element(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True)
class Column(Element, lang.Final):
    name: str
    type: Datatype


@dc.dataclass(frozen=True)
class PrimaryKey(Element, lang.Final):
    columns: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Index(Element, lang.Final):
    columns: ta.Sequence[str]
    name: str | None = None


#


@dc.dataclass(frozen=True)
class IdIntegerPrimaryKey(Element, lang.Final):
    pass


#


@dc.dataclass(frozen=True)
class CreatedAt(Element, lang.Final):
    pass


@dc.dataclass(frozen=True)
class UpdatedAt(Element, lang.Final):
    pass


@dc.dataclass(frozen=True)
class UpdatedAtTrigger(Element, lang.Final):
    column: str


@dc.dataclass(frozen=True)
class CreatedAtUpdatedAt(Element, lang.Final):
    pass


#


@dc.dataclass(frozen=True)
class Elements(ta.Sequence[Element], lang.Final):
    lst: ta.Sequence[Element]

    def __iter__(self) -> ta.Iterator[Element]:
        return iter(self.lst)

    def __getitem__(self, index: ta.Any) -> Element:
        return self.lst[index]

    def __len__(self) -> int:
        return len(self.lst)

    @lang.cached_property
    def by_type(self) -> col.DynamicTypeMap[Element]:
        return col.DynamicTypeMap(self.lst)


@dc.dataclass(frozen=True)
class TableDef(lang.Final):
    name: str
    elements: Elements


#


def lower_table_elements(td: TableDef) -> TableDef:
    todo: list[Element] = list(td.elements)[::-1]
    out: list[Element] = []

    while todo:
        match (e := todo.pop()):
            case Column() | PrimaryKey():
                out.append(e)

            case IdIntegerPrimaryKey():
                out.extend([
                    Column('id', Integer()),
                    PrimaryKey(['id']),
                ])

            case CreatedAt():
                out.append(Column('created_at', Timestamp()))

            case UpdatedAt():
                out.extend([
                    Column('updated_at', Timestamp()),
                    UpdatedAtTrigger('updated_at'),
                ])

            case CreatedAtUpdatedAt():
                todo.extend([
                    CreatedAt(),
                    UpdatedAt(),
                ][::-1])

            case _:
                raise TypeError(e)

    return dc.replace(td, elements=Elements(out))


#


def _main() -> None:
    users = TableDef(
        'users',
        Elements([
            IdIntegerPrimaryKey(),
            CreatedAtUpdatedAt(),
            Column('name', String()),
        ]),
    )
    print(users)

    users_lowered = lower_table_elements(users)
    print(users_lowered)
    print(users_lowered.elements.by_type[Column])


if __name__ == '__main__':
    _main()
