import datetime
import logging
import os

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa

from omlish import check
from omlish import inject as inj
from omlish import lang
from omlish import secrets as sec
from omlish import sql
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omserv.apps.base import BaseServerUrl
from omserv.apps.routes import RouteHandlerApp
from omserv.apps.templates import J2Templates
from omserv.dbs import get_db_url


log = logging.getLogger(__name__)


def _build_engine():
    e = sql.async_adapt(saa.create_async_engine(get_db_url(), echo=True))
    log.info('Sqlalchemy engine created: %r', e)

    @sa.event.listens_for(e.underlying.sync_engine, 'engine_disposed')
    def on_disposed(_e):
        check.is_(e.underlying.sync_engine, _e)
        log.info('Sqlalchemy engine disposed: %r', e)

    return e


def bind_dbs() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(
            sql.AsyncEngine,
            to_fn=inj.make_async_managed_provider(
                _build_engine,
                lambda e: lang.a_defer(e.dispose()),  # noqa
            ),
            singleton=True,
        ),
    )
