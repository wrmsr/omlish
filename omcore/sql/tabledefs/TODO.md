- ELEMENTS ARE TYPEDVALUES
- dtypes:
  - uuid
  - jsonb
  - string len?
- QualifiedName
- hybrid dataclass scheme
- sqlite without sqlalchemy
- declarative lol

```
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
```
