import contextlib
import typing as ta
import urllib.parse

from ... import check
from ... import lang
from ... import sql
from ...sql.tests.harness import HarnessDbs
from ...testing import pytest as ptu
from ..sql import SqlStore
from .models import build_registry
from .test_orm import _test_orm


##


@ptu.skip.if_cant_import('pymysql')
def test_pymysql(harness) -> None:
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

    registry = build_registry()
    store = SqlStore(
        registry,
        adb,
        tabledef_renderer=sql.be.mysql.td.MysqlTabledefRenderer(),
        tabledef_create_options=sql.td.Renderer.CreateOptions(
            drop_if_exists=True,
        ),
    )

    lang.sync_await(_test_orm(store, registry))
