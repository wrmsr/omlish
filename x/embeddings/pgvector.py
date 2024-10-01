"""
https://www.reddit.com/r/PostgreSQL/comments/1fq6s35/18_months_of_pgvector_learnings_in_47
"""
import contextlib
import os.path

import sqlalchemy as sa

from omlish import check
from omlish import lang
from omlish.docker.tests.services import ComposeServices
from omlish.sql import dbs
from omlish.sql.tests.dbs import Dbs


def _main():
    cs = ComposeServices(
        config_file_path=os.path.join(os.path.dirname(__file__), '../../docker/compose.yml'),
    )
    ds = Dbs(cs)

    url = check.isinstance(check.isinstance(ds.specs()['pgvector'].loc, dbs.UrlDbLoc).url, str)
    url = dbs.set_url_engine(url, 'postgresql+pg8000')

    with contextlib.ExitStack() as es:
        engine = sa.create_engine(url, echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.connect() as conn:
            result = conn.execute(sa.select(1))
            rows = list(result.fetchall())
            assert len(rows) == 1


if __name__ == '__main__':
    _main()
