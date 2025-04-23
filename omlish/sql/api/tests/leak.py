import sqlite3

from .. import funcs
from ..dbapi import DbapiDb
from ..resources import set_resource_debug


##


def _main() -> None:
    set_resource_debug(True)

    with DbapiDb(lambda: sqlite3.connect(':memory:')) as db:
        with db.connect() as conn:
            print(funcs.query(conn, 'select 1'))


if __name__ == '__main__':
    _main()
