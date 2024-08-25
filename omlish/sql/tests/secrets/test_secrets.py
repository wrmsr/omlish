"""
https://www.postgresql.org/docs/current/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY

https://www.postgresql.org/docs/current/pgcrypto.html

======

create database omlish;
grant connect on database omlish to postgres;
use omlish;

--

PGPASSWORD=secrets_owner_password .venv/bin/pgcli --host 127.0.0.1 --port 35225 --user secrets_owner --dbname omlish
PGPASSWORD=secrets_reader_password .venv/bin/pgcli --host 127.0.0.1 --port 35225 --user secrets_reader --dbname omlish

set search_path to secrets, public;

"""
import contextlib

import sqlalchemy as sa

from ... import check
from ... import lang
from ...testing import pytest as ptu
from ..dbs import UrlDbLoc
from ..dbs import set_url_engine
from .dbs import Dbs


@ptu.skip_if_cant_import('pg8000')
def test_postgres_pg8000(harness) -> None:
    url = check.isinstance(check.isinstance(harness[Dbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    url = set_url_engine(url, 'postgresql+pg8000')

    with contextlib.ExitStack() as es:
        engine = sa.create_engine(url, echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.begin() as conn:
            meta.drop_all(bind=conn)
            meta.create_all(bind=conn)

            conn.execute(
                t1.insert(), [
                    {'name': 'some name 1'},
                    {'name': 'some name 2'},
                ],
            )

        with engine.connect() as conn:
            result = conn.execute(sa.select(t1).where(t1.c.name == 'some name 1'))
            rows = list(result.fetchall())
            assert len(rows) == 1
            assert rows[0].name == 'some name 1'
