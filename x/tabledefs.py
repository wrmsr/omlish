"""
TODO:
 - QualifiedName
 - datatypes
"""
import dataclasses as dc
import typing as ta

from omlish import lang


class TableElement(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class TableColumn(TableElement, lang.Final):
    name: str
    type: str

@dc.dataclass(frozen=True)
class TablePrimaryKey(TableElement, lang.Final):
    columns: ta.Sequence[str]


@dc.dataclass(frozen=True)
class TableDef(lang.Final):
    name: str
    elements: ta.Sequence[TableElement]


def _main() -> None:
    users_table_def = TableDef(
        'users',
        [
            TableColumn('id', 'integer'),
            TableColumn('name', 'string'),
        ],
    )


if __name__ == '__main__':
    _main()
