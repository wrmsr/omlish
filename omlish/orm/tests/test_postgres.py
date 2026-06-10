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


@ptu.skip.if_cant_import('pg8000')
def test_pg8000(harness, exit_stack) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, sql.UrlDbLoc).url, str)
    p_u = urllib.parse.urlparse(url)

    import pg8000

    db = sql.api.DbapiDb(
        sql.api.ClosingDbapiConnector(
            pg8000.connect,
            p_u.username,
            host=p_u.hostname,
            port=p_u.port,
            password=p_u.password,
        ),
        adapter=sql.be.postgres.adapters.postgres_adapter(),
    )

    adb = sql.api.SyncToAsyncDb(sql.api.ImmediateSyncToAsyncRunner, db)

    registry = build_registry()
    store = SqlStore(
        registry,
        adb,
        tabledef_renderer=sql.be.postgres.td.PostgresStatementRenderer(),
        tabledef_create_options=sql.td.StatementRenderer.CreateOptions(
            drop_if_exists=True,
        ),
    )

    lang.sync_await(_test_orm(store, registry))
