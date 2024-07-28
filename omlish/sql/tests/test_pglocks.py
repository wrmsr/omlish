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
import hashlib
import struct
import typing as ta

import sqlalchemy as sa
import sqlalchemy.ext.compiler


def make_pg_lock_name(s: str) -> int:
    return struct.unpack('>q', hashlib.sha1(s.encode()).digest()[:8])[0]  # noqa


class pg_lock_name(sa.sql.expression.FunctionElement):  # noqa
    s: str


@sa.ext.compiler.compiles(pg_lock_name)
def _pg_lock_name(
        element: pg_lock_name,
        compiler: sa.sql.compiler.SQLCompiler,
        **kw: ta.Any,
) -> str:
    # FIXME: escape lol
    return f"trim(leading '\\' from substr(digest('{element.s}', 'sha1'), 1, 8)::text)::bit(64)::bigint"
