import contextlib
import typing as ta
import urllib.parse

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import orm
from ... import sql
from ...sql.tests.harness import HarnessDbs
from ...testing import pytest as ptu
from ..sql import SqlStore


##


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class Thing:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key[int])

    n: int


@ptu.skip.if_cant_import('pymysql')
def test_pymysql(harness) -> None:
    # A deliberately minimal, index-free model so this exercises exactly the mysql auto-key insert path - which has no
    # RETURNING and instead reads the id back via the dialect's last_insert_id() query - rather than the broader,
    # still-incomplete mysql DDL story (indexed text columns etc).

    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['mysql'].loc, sql.UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import pymysql

    # ensure the test database exists (own-and-nuke dev instance)
    with contextlib.closing(pymysql.connect(
        host=p_u.hostname,
        port=check.not_none(p_u.port),
        user=p_u.username,
        password=check.not_none(p_u.password),
    )) as c:
        with c.cursor() as cur:
            cur.execute('create database if not exists omlish_test')
        c.commit()

    db = sql.api.DbapiDb(
        sql.api.ClosingDbapiConnector(
            ta.cast(ta.Any, pymysql.connect),  # typed pymysql.connect won't unify with the connector ParamSpec
            host=p_u.hostname,
            port=check.not_none(p_u.port),
            user=p_u.username,
            password=check.not_none(p_u.password),
            database='omlish_test',
            autocommit=True,
        ),
        adapter=sql.be.mysql.adapters.mysql_adapter(),
    )

    adb = sql.api.SyncToAsyncDb(sql.api.ImmediateSyncToAsyncRunner, db)

    registry = orm.registry(orm.mapper(Thing))
    store = SqlStore(
        registry,
        adb,
        tabledef_renderer=sql.be.mysql.td.MysqlStatementRenderer(),
        tabledef_create_options=sql.td.StatementRenderer.CreateOptions(
            drop_if_exists=True,
        ),
    )

    async def inner() -> None:
        async with orm.session(registry, store):
            t1 = Thing(n=42)
            t2 = Thing(n=43)
            await orm.add(t1)
            await orm.add(t2)

            # neither insert uses RETURNING; each auto key is read back via select last_insert_id()
            [g1] = await orm.query(Thing, n=42)
            [g2] = await orm.query(Thing, n=43)
            assert g1.id is not None
            assert g2.id is not None
            assert g1.id != g2.id
            assert await orm.get(Thing, g1.id) is g1

    lang.sync_await(inner())
