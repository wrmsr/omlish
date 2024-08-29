"""
TODO:
 - QualifiedName
 - hybrid dataclass scheme

==

@td.tableclass([
    IdIntegerPrimaryKey(),
    CreatedAtUpdatedAt(),
])
@dc.dataclass(frozen=True)
class User(lang.Final):
    id: int

    created_at: datetime.datetime
    updated_at: datetime.datetime

    name: str

==

@td.tableclass([
    IdIntegerPrimaryKey(),
    CreatedAtUpdatedAt(),
])
@dc.dataclass(frozen=True)
class BaseTable(lang.Abstract):
    id: int

    created_at: datetime.datetime
    updated_at: datetime.datetime

@td.tableclass('user')
@dc.dataclass(frozen=True)
class User(BaseTable, lang.Final):
    name: str

"""
import typing as ta

import sqlalchemy as sa
import sqlalchemy.sql.schema

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json


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
class Datetime(Datatype, lang.Singleton):
    pass


#


class Element(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True)
class Column(Element, lang.Final):
    name: str
    type: Datatype
    nullable: bool = dc.field(default=False, kw_only=True)
    default: lang.Maybe[ta.Any] = dc.field(default=lang.empty(), kw_only=True)


@dc.dataclass(frozen=True)
class PrimaryKey(Element, lang.Final):
    columns: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Index(Element, lang.Final):
    columns: ta.Sequence[str] = dc.xfield(coerce=col.seq)
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
    lst: ta.Sequence[Element] = dc.xfield(coerce=col.seq_of(check.of_isinstance(Element)))

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
                out.append(Column('created_at', Datetime()))

            case UpdatedAt():
                out.extend([
                    Column('updated_at', Datetime()),
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


def build_sa_table(
        td: TableDef,
        *,
        metadata: sa.MetaData | None = None,
        **kwargs: ta.Any
) -> sa.Table:
    items: list[sa.sql.schema.SchemaItem] = []

    return sa.Table(
        td.name,
        metadata if metadata is not None else sa.MetaData(),
        *items,
        **kwargs,
    )


#


def _main() -> None:
    def install_msh_poly(cls: type) -> None:
        p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
        msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(p)]
        msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(p)]

    install_msh_poly(Datatype)
    install_msh_poly(Element)

    users = TableDef(
        'users',
        Elements([
            IdIntegerPrimaryKey(),
            CreatedAtUpdatedAt(),
            Column('name', String()),
        ]),
    )
    print(users_json := json.dumps_pretty(msh.marshal(users)))

    users2 = msh.unmarshal(json.loads(users_json), TableDef)
    assert users2 == users

    users_lowered = lower_table_elements(users)
    print(json.dumps_pretty(msh.marshal(users_lowered)))

    print(users_lowered.elements.by_type[Column])


if __name__ == '__main__':
    _main()
