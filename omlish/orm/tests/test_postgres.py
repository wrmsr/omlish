# import contextlib
# import typing as ta
# import concurrent.futures as cf
# import urllib.parse
# from ...asyncs.asyncio import all as au
#
# from ... import lang
# from ... import check
# from ...testing import pytest as ptu
# from ... import sql
# from ...sql.tests.harness import HarnessDbs
# from .test_orm import _test_orm
# from ..sql import SqlStore
# from .models import build_registry
#
#
# ##
#
#
# @ptu.skip.if_cant_import('pg8000')
# def test_pg8000(harness, exit_stack) -> None:
#     url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, sql.UrlDbLoc).url, str)
#     p_u = urllib.parse.urlparse(url)
#
#     import pg8000
#
#     db = sql.api.DbapiDb(lambda: contextlib.closing(pg8000.connect(  # noqa
#         p_u.username,
#         host=p_u.hostname,
#         port=p_u.port,
#         password=p_u.password,
#     )))
#
#     exe = exit_stack.enter_context(cf.ThreadPoolExecutor(max_workers=1))
#
#     adb = sql.api.SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))), db)
#
#     registry = build_registry()
#     store = SqlStore(registry, adb)
#
#     lang.sync_await(_test_orm(store, registry))
