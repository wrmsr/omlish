import urllib.parse

from ..... import check
from .....testing import pytest as ptu
from ....api import querierfuncs as qf
from ....api.dbapi import ClosingDbapiConnector
from ....api.dbapi import DbapiDb
from ....dbs import UrlDbLoc
from ....tests.harness import HarnessDbs


##


@ptu.skip.if_cant_import('pg8000')
def test_pg8000(harness, exit_stack) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import pg8000

    db = DbapiDb(ClosingDbapiConnector(
        pg8000.connect,
        p_u.username,
        host=p_u.hostname,
        port=p_u.port,
        password=p_u.password,
    ))

    conn = exit_stack.enter_context(db.connect())

    for q in [
        'select 1',
        'select 1 union select 2',
        # 'select 1, 2 union select 3, 4',
    ]:
        with qf.query(conn, q) as rows:
            vals = []
            for row in rows:
                vals.append(tuple(row.values))
                print(row)

        print(vals)
