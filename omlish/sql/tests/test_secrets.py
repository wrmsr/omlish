"""
https://www.postgresql.org/docs/current/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY

==

CREATE FUNCTION check_password(uname TEXT, pass TEXT)
RETURNS BOOLEAN AS $$
DECLARE passed BOOLEAN;
BEGIN
        SELECT  (pwd = $2) INTO passed
        FROM    pwds
        WHERE   username = $1;

        RETURN passed;
END;
$$  LANGUAGE plpgsql
    SECURITY DEFINER
    -- Set a secure search_path: trusted schema(s), then 'pg_temp'.
    SET search_path = admin, pg_temp;

==

BEGIN;
CREATE FUNCTION check_password(uname TEXT, pass TEXT) ... SECURITY DEFINER;
REVOKE ALL ON FUNCTION check_password(uname TEXT, pass TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION check_password(uname TEXT, pass TEXT) TO admins;
COMMIT;

======

create database omlish;
grant connect on database omlish to postgres;
use omlish;

--

drop schema if exists secrets;

drop user if exists secrets_reader;
drop user if exists secrets_owner;

do $$ declare
  r text;
begin
  foreach r in array array[
      'secrets_owner_role',
      'secrets_reader_role'
  ] loop
    if exists (select 1 from pg_roles where rolname = r) then
      execute format('drop owned by %s', r);
    end if;
  end loop;
end $$;

drop role if exists secrets_reader_role;
drop role if exists secrets_owner_role;

--

create role secrets_owner_role;
grant connect on database omlish to secrets_owner_role;
create user secrets_owner with password 'secrets_owner_password';
grant secrets_owner_role to secrets_owner;

create role secrets_reader_role;
grant connect on database omlish to secrets_reader_role;
create user secrets_reader with password 'secrets_reader_password';
grant secrets_reader_role to secrets_reader;

create schema secrets authorization secrets_owner_role;

create table secrets.secrets (
  key varchar(50) primary key not null,
  value varchar(1024) not null,
  created_at timestamp not null default now()
);
alter table secrets.secrets owner to secrets_owner_role;

create table secrets.secrets_access (
  key varchar(50) primary key not null,
  value varchar(1024) not null
);
alter table secrets.secrets_access owner to secrets_owner_role;

--

PGPASSWORD=secrets_owner_password .venv/bin/pgcli --host 127.0.0.1 --port 35225 --user secrets_owner --dbname omlish
PGPASSWORD=secrets_reader_password .venv/bin/pgcli --host 127.0.0.1 --port 35225 --user secrets_reader --dbname omlish

set search_path to secrets, public;

--

create or replace function barf() returns varchar as $$ begin
  raise notice 'c %', current_user;
  raise notice 's %', session_user;
  raise notice 'i %', inet_client_addr();
  return null;
end $$
  language plpgsql
  security definer;

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
