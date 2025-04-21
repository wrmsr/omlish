import logging

import sqlalchemy as sa
import sqlalchemy.event
import sqlalchemy.ext.asyncio as saa

from omlish import check
from omlish import inject as inj
from omlish import lang
from omlish.secrets import all as sec
from omlish.sql import alchemy as sau
from omlish.sql import dbs


log = logging.getLogger(__name__)


def _build_engine(
        spec: dbs.DbSpec,
        secrets: sec.Secrets = sec.EMPTY_SECRETS,
) -> sau.AsyncEngine:
    check.equal(spec.type, dbs.DbTypes.POSTGRES)
    ul = check.isinstance(spec.loc, dbs.UrlDbLoc)
    e = sau.async_adapt(saa.create_async_engine(secrets.fix(ul.url).reveal(), echo=True))

    log.info('Sqlalchemy engine created: %r', e)

    @sa.event.listens_for(e.underlying.sync_engine, 'engine_disposed')
    def on_disposed(_e):
        check.is_(e.underlying.sync_engine, _e)
        log.info('Sqlalchemy engine disposed: %r', e)

    return e


def bind_dbs() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(
            dbs.DbSpec(
                'primary',
                dbs.DbTypes.POSTGRES,
                dbs.UrlDbLoc(sec.SecretRef('db_url')),
            ),
        ),

        inj.bind(
            sau.AsyncEngine,
            to_fn=inj.make_async_managed_provider(
                _build_engine,
                lambda e: lang.adefer(e.dispose()),  # noqa
            ),
            singleton=True,
        ),
    )
