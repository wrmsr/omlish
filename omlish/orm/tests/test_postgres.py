# import concurrent.futures as cf
# import contextlib
# import typing as ta
# import urllib.parse
#
# from ... import check
# from ... import lang
# from ... import sql
# from ...asyncs.asyncio import all as au
# from ...sql.tests.harness import HarnessDbs
# from ...testing import pytest as ptu
# from ..sql import SqlStore
# from .models import build_registry
# from .test_orm import _test_orm
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
#     adb = sql.api.SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToExecutor(exe))), db)
#
#     registry = build_registry()
#     store = SqlStore(registry, adb)
#
#     lang.sync_await(_test_orm(store, registry))
