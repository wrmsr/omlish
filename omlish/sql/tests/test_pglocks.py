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
