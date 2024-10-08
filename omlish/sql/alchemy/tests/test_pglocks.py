"""
TODO:
 - lockinfo table: hash -> description str, auto-delete when no advisory with hash in pg_locks (insert transactional w/ lock acq)

See:
 - https://www.postgresql.org/docs/16/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS

==

postgres@omlish-1:postgres> create extension pgcrypto;
CREATE EXTENSION

postgres@omlish-1:postgres> select trim(leading '\' from substr(digest('foo', 'sha1'), 1, 8)::text)::bit(64)::bigint
+--------------------+
| ltrim              |
|--------------------|
| 859844163007352795 |
+--------------------+
SELECT 1
Time: 0.030s

==

In [9]: import struct, hashlib

In [14]: struct.unpack('>q', hashlib.sha1(b'foo').digest()[:8])
Out[14]: (859844163007352795,)

"""  # noqa
import contextlib
import hashlib
import struct
import typing as ta

import sqlalchemy as sa
import sqlalchemy.ext.compiler

from .... import check
from .... import lang
from ....diag import pydevd as pdu  # noqa
from ...dbs import UrlDbLoc
from ...dbs import set_url_engine
from ...tests.harness import HarnessDbs


def make_pg_lock_name(s: str) -> int:
    return struct.unpack('>q', hashlib.sha1(s.encode()).digest()[:8])[0]  # noqa


class pg_lock_name(sqlalchemy.sql.expression.UnaryExpression):  # noqa
    inherit_cache = True


@sa.ext.compiler.compiles(pg_lock_name)
def _compile_pg_lock_name(
        element: pg_lock_name,
        compiler: sa.sql.compiler.SQLCompiler,
        **kw: ta.Any,
) -> str:
    return "trim(leading '\\' from substr(digest(%s, 'sha1'), 1, 8)::text)::bit(64)::bigint" % \
        (element.element._compiler_dispatch(compiler),)  # noqa


def test_pglocks(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    url = set_url_engine(url, 'postgresql+pg8000')

    with contextlib.ExitStack() as es:
        engine = sa.create_engine(url, echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.begin() as conn:
            conn.execute(sa.text('create extension if not exists pgcrypto'))

            lock_name = 'foo'

            py_key = make_pg_lock_name(lock_name)
            [pg_key] = conn.execute(sa.select(pg_lock_name(sa.literal(lock_name)))).fetchone()  # type: ignore
            assert py_key == pg_key
