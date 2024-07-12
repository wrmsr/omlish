import dataclasses as dc

from .. import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class DbType:
    name: str
    dialect_name: str

    default_port: int | None = None


class DbTypes(lang.Namespace):
    MYSQL = DbType(
        name='mysql',
        dialect_name='mysql',
        default_port=3306,
    )

    POSTGRES = DbType(
        name='postgres',
        dialect_name='postgresql',
        default_port=5432,
    )

    SQLITE = DbType(
        name='sqlite',
        dialect_name='sqlite',
    )


##


class DbLoc(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class UrlDbLoc(DbLoc, lang.Final):
    url: str


@dc.dataclass(frozen=True)
class HostDbLoc(DbLoc, lang.Final):
    host: str
    port: int | None = None

    username: str | None = None
    password: str | None = dc.field(default=None, repr=False)


##


@dc.dataclass(frozen=True)
class DbSpec:
    name: str
    type: DbType
    loc: DbLoc
