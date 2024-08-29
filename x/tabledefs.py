"""
TODO:
 - QualifiedName
 - datatypes
"""
import dataclasses as dc
import typing as ta

from omlish import lang


#


class TableElement(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True)
class TableColumn(TableElement, lang.Final):
    name: str
    type: str


@dc.dataclass(frozen=True)
class TablePrimaryKey(TableElement, lang.Final):
    columns: ta.Sequence[str]


#


@dc.dataclass(frozen=True)
class IdIntegerPrimaryKey(TableElement, lang.Final):
    pass


#


@dc.dataclass(frozen=True)
class TableDef(lang.Final):
    name: str
    elements: ta.Sequence[TableElement]


#


def lower_table_elements(td: TableDef) -> TableDef:
    es: list[TableElement] = []
    for e in td.elements:
        match e:
            case TableColumn() | TablePrimaryKey():
                es.append(e)
            case IdIntegerPrimaryKey():
                es.extend([
                    TableColumn('id', 'integer'),
                    TablePrimaryKey(['id']),
                ])
            case _:
                raise TypeError(e)
    return dc.replace(td, elements=es)


#


def _main() -> None:
    users = TableDef(
        'users',
        [
            IdIntegerPrimaryKey(),
            TableColumn('name', 'string'),
        ],
    )
    print(users)

    users_lowered = lower_table_elements(users)
    print(users_lowered)


if __name__ == '__main__':
    _main()
