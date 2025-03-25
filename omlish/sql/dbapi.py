"""
https://peps.python.org/pep-0249/

==

apilevel = '2.0'

paramstyle:
 qmark - Question mark style, e.g. ...WHERE name=?
 numeric - Numeric, positional style, e.g. ...WHERE name=:1
 named - Named style, e.g. ...WHERE name=:name
 format - ANSI C printf format codes, e.g. ...WHERE name=%s
 pyformat - Python extended format codes, e.g. ...WHERE name=%(name)s

Exception
| Warning
| Error
 | InterfaceError
 | DatabaseError
  | DataError
  | OperationalError
  | IntegrityError
  | InternalError
  | ProgrammingError
  | NotSupportedError

Date(year, month, day)
Time(hour, minute, second)
Timestamp(year, month, day, hour, minute, second)
DateFromTicks(ticks)
TimeFromTicks(ticks)
TimestampFromTicks(ticks)
Binary(string)

STRING type
BINARY type
NUMBER type
DATETIME type
ROWID type
"""
import dataclasses as dc
import enum

from .. import lang
from .params import ParamStyle


##


class DbapiDialect(enum.Enum):
    SQLITE = 'sqlite'
    MYSQL = 'mysql'
    POSTGRES = 'postgres'
    SNOWFLAKE = 'snowflake'


@dc.dataclass(frozen=True, kw_only=True)
class DbapiDriver:
    name: str
    dialect: DbapiDialect
    param_style: ParamStyle

    package_name: str | None = None
    module_name: str | None = None


class DbapiDrivers(lang.Namespace):

    ##
    # sqlite

    SQLITE3 = DbapiDriver(
        name='sqlite3',
        dialect=DbapiDialect.SQLITE,
        param_style=ParamStyle.QMARK,
    )

    SQLEAN = DbapiDriver(
        name='sqlean',
        dialect=DbapiDialect.SQLITE,
        param_style=ParamStyle.QMARK,
        package_name='sqlean.py',
    )

    DUCKDB = DbapiDriver(
        name='duckdb',
        dialect=DbapiDialect.SQLITE,
        param_style=ParamStyle.QMARK,
    )

    ##
    # mysql

    PYMYSQL = DbapiDriver(
        name='pymysql',
        dialect=DbapiDialect.MYSQL,
        param_style=ParamStyle.PYFORMAT,
    )

    MYSQL = DbapiDriver(
        name='mysql',
        dialect=DbapiDialect.MYSQL,
        param_style=ParamStyle.PYFORMAT,
        package_name='mysql-connector-python',
        module_name='mysql.connector',
    )

    MYSQLCLIENT = DbapiDriver(
        name='mysqlclient',
        dialect=DbapiDialect.MYSQL,
        param_style=ParamStyle.FORMAT,
        package_name='mysqlclient',
        module_name='MySQLdb',
    )

    ##
    # postgres

    PG8000 = DbapiDriver(
        name='pg8000',
        dialect=DbapiDialect.POSTGRES,
        param_style=ParamStyle.FORMAT,
    )

    PSYCOPG2 = DbapiDriver(
        name='psycopg2',
        dialect=DbapiDialect.POSTGRES,
        param_style=ParamStyle.PYFORMAT,
    )

    PSYCOPG = DbapiDriver(
        name='psycopg',
        dialect=DbapiDialect.POSTGRES,
        param_style=ParamStyle.PYFORMAT,
    )

    ##
    # snowflake

    SNOWFLAKE = DbapiDriver(
        name='snowflake',
        dialect=DbapiDialect.SNOWFLAKE,
        param_style=ParamStyle.PYFORMAT,
        package_name='snowflake-connector-python',
        module_name='snowflake.connector',
    )
