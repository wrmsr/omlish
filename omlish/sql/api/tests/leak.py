import sqlite3

from ....resources import set_resource_debug
from .. import querierfuncs as qf
from ..dbapi import DbapiDb


##


def _main() -> None:
    set_resource_debug(True)

    with DbapiDb(lambda: sqlite3.connect(':memory:', autocommit=True)) as db:
        with db.connect() as conn:
            print(qf.query(conn, 'select 1'))


if __name__ == '__main__':
    _main()
