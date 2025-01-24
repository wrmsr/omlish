import typing as ta
import urllib.parse

from .. import dataclasses as dc
from .. import lang
from ..secrets import all as sec


##


@dc.dataclass(frozen=True, kw_only=True)
class DbType(lang.Final):
    name: str
    dialect_name: str

    default_port: int | None = None


class DbTypes(lang.Namespace, lang.Final):
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


class DbLoc(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class UrlDbLoc(DbLoc, lang.Final):
    url: sec.SecretRefOrStr = dc.xfield() | sec.secret_field


@dc.dataclass(frozen=True)
class HostDbLoc(DbLoc, lang.Final):
    host: str
    port: int | None = None

    username: str | None = None
    password: sec.SecretRefOrStr | None = dc.xfield(default=None) | sec.secret_field


##


@dc.dataclass(frozen=True)
class DbSpec(lang.Final):
    name: str
    type: DbType
    loc: DbLoc


##


def rebuild_url(url: str, fn: ta.Callable[[urllib.parse.ParseResult], urllib.parse.ParseResult]) -> str:
    if '://' in url:
        engine, _, url = url.partition('://')
        url = 'sql://' + url
    else:
        engine = None
    parsed = urllib.parse.urlparse(url)
    parsed = fn(parsed)
    if engine is not None and parsed.scheme == 'sql':
        parsed = parsed._replace(scheme=engine)
    return urllib.parse.urlunparse(parsed)  # noqa


def set_url_engine(url: str, engine: str) -> str:
    return rebuild_url(url, lambda parsed: parsed._replace(scheme=engine))  # noqa


def set_url_database(url: str, database: str) -> str:
    return rebuild_url(url, lambda parsed: parsed._replace(path='/' + database))  # noqa
