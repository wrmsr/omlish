import logging

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa

from omlish import check
from omlish import inject as inj
from omlish import lang
from omlish import secrets as sec
from omlish import sql
from omserv.dbs import get_db_url


log = logging.getLogger(__name__)


def _build_engine(
        secrets: sec.Secrets = sec.EMPTY_SECRETS,
) -> sql.AsyncEngine:
    e = sql.async_adapt(saa.create_async_engine(get_db_url(), echo=True))
    log.info('Sqlalchemy engine created: %r', e)

    @sa.event.listens_for(e.underlying.sync_engine, 'engine_disposed')
    def on_disposed(_e):
        check.is_(e.underlying.sync_engine, _e)
        log.info('Sqlalchemy engine disposed: %r', e)

    return e


def bind_dbs() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(sec.Secrets, to_const=sec.SimpleSecrets({
            'session_secret_key': 'secret-key-goes-here',  # noqa
        })),

        inj.bind(
            sql.AsyncEngine,
            to_fn=inj.make_async_managed_provider(
                _build_engine,
                lambda e: lang.a_defer(e.dispose()),  # noqa
            ),
            singleton=True,
        ),
    )
